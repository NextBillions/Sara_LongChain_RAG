import os
import time

from src.models.embedding import EmbeddingModel
from pymilvus import MilvusClient, MilvusException
from src.utils import setup_logger, hashstr
logger = setup_logger("KnowledgeBase")


class KnowledgeBase:

    def __init__(self, config=None, embed_model=None) -> None:
        self.config = config or {}
        assert embed_model, "embed_model=None"
        self.embed_model = embed_model

        self.client = None
        if not self.connect_to_milvus():
            raise ConnectionError("Failed to connect to Milvus")

    def connect_to_milvus(self):
        """连接到 Milvus 服务"""
        try:
            uri = os.getenv('MILVUS_URI', self.config.get('milvus_uri', "http://192.168.32.100:19530"))
        
            self.client = MilvusClient(
                self.client = MilvusClient(uri=uri)
                timeout=30  # 增加超时时间
            )
            
            # 测试连接
            try:
                collections = self.client.list_collections()
                logger.info(f"Successfully connected to Milvus. Collections: {collections}")
                return True
            except Exception as e:
                logger.error(f"Failed to list collections: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {str(e)}")
            return False

    def get_collection_names(self):
        """获取所有集合名称"""
        try:
            return self.client.list_collections()
        except Exception as e:
            logger.error(f"Failed to list collections: {str(e)}")
            return []

    def get_collections(self):
        collections_name = self.client.list_collections()
        collections = []
        for collection_name in collections_name:
            collection = self.get_collection_info(collection_name)
            collections.append(collection)

        return collections

    def get_collection_info(self, collection_name):
        """获取集合信息"""
        try:
            if not self.client.has_collection(collection_name):
                return {"count": 0, "dimension": 0}
            
            collection_info = self.client.describe_collection(collection_name)
            stats = self.client.get_collection_stats(collection_name)
            
            return {
                "count": stats.get("row_count", 0),
                "dimension": collection_info.get("fields", [{}])[1].get("dim", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get collection info for {collection_name}: {str(e)}")
            return {"count": 0, "dimension": 0}

    def add_collection(self, collection_name, dimension):
        """添加新的集合"""
        try:
            logger.info(f"Creating collection: {collection_name} with dimension: {dimension}")
            
            schema = {
                "fields": [
                    {
                        "name": "id",
                        "dtype": "int64",
                        "is_primary": True,
                        "auto_id": True
                    },
                    {
                        "name": "vector",
                        "dtype": "float_vector",
                        "dim": dimension
                    },
                    {
                        "name": "text",
                        "dtype": "varchar",
                        "max_length": 65535
                    },
                    {
                        "name": "file_id",
                        "dtype": "varchar",
                        "max_length": 255
                    },
                    {
                        "name": "hash",
                        "dtype": "varchar",
                        "max_length": 255
                    }
                ]
            }

            # 创建集合
            self.client.create_collection(
                collection_name=collection_name,
                schema=schema
            )

            # 创建索引
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }

            self.client.create_index(
                collection_name=collection_name,
                field_name="vector",
                index_params=index_params
            )
            
            logger.info(f"Successfully created collection and index: {collection_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {str(e)}")
            raise

    def add_documents(self, docs, collection_name, **kwargs):
        """添加已经分块之后的文本"""
        # 检查 collection 是否存在
        import random
        if not self.client.has_collection(collection_name=collection_name):
            logger.error(f"Collection {collection_name} not found, create it")
            # self.add_collection(collection_name)

        vectors = self.embed_model.encode(docs)

        data = [{
            "id": int(random.random() * 1e12),
            "vector": vectors[i],
            "text": docs[i],
            "hash": hashstr(docs[i], with_salt=True),
            **kwargs} for i in range(len(vectors))]

        res = self.client.insert(collection_name=collection_name, data=data)
        return res

    def search(self, query, collection_name, limit=3):

        query_vectors = self.embed_model.encode_queries([query])
        return self.search_by_vector(query_vectors[0], collection_name, limit)

    def search_by_vector(self, vector, collection_name, limit=3):
        res = self.client.search(
            collection_name=collection_name,  # target collection
            data=[vector],  # query vectors
            limit=limit,  # number of returned entities
            output_fields=["text", "file_id"],  # specifies fields to be returned
        )

        return res[0]

    def examples(self, collection_name, limit=20):
        res = self.client.query(
            collection_name=collection_name,
            limit=10,
            output_fields=["id", "text"],
        )
        return res

    def search_by_id(self, collection_name, id, output_fields=["id", "text"]):
        res = self.client.get(collection_name, id, output_fields=output_fields)
        return res
