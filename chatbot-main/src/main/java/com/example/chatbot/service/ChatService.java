package com.example.chatbot.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Service;
import org.springframework.util.StreamUtils;
import org.yaml.snakeyaml.Yaml;

import javax.annotation.PostConstruct;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.regex.Pattern;

@Service
public class ChatService {

    @Value("classpath:prompts.yaml")
    private Resource promptsFile;

    private Map<String, Map<String, String>> intents;

    @PostConstruct
    public void loadPrompts() throws Exception {
        String content = StreamUtils.copyToString(promptsFile.getInputStream(), StandardCharsets.UTF_8);
        Yaml yaml = new Yaml();
        intents = yaml.load(content);
    }

    public String getReply(String sessionId, String message) {
        for (Map.Entry<String, Map<String, String>> entry : intents.entrySet()) {
            String intent = entry.getKey();
            String pattern = entry.getValue().get("pattern");
            if (Pattern.matches(pattern, message)) {
                String prompt = entry.getValue().get("systemPrompt");
                return callDeepSeek(prompt + "\nUser: " + message);
            }
        }
        return "I'm not sure how to respond to that.";
    }

    private String callDeepSeek(String prompt) {
        // Replace this stub with actual HTTP call to DeepSeek API
        return "[Simulated Response from DeepSeek for prompt: " + prompt + "]";
    }
}