def query_ollama_with_vision(prompt, system_prompt=None, image_data=None):
    """Query the Ollama API for AI responses"""
    if not ai_config.get("AI_ENABLED", True):
        return "AI is currently disabled."

    model_name = ai_config["VISION_MODEL_NAME"] if image_data else ai_config["MODEL_NAME"]
    
    data = {
        "model": model_name,
        "prompt": prompt,
        "stream": False if image_data else True,
        "options": {
        "num_ctx": 4080,
        "num_predict": 350,
        "temperature": 0.7,
        "top_p": 0.9,
        "num_thread": 4
    }
}
    if system_prompt:
        data["system"] = system_prompt

    if image_data:
        data["images"] = [image_data]

    try:
        response = requests.post(ai_config["MODEL_API_URL"], json=data, timeout=None)
    except Exception as e:
        print(f"AI Error: {e}")
        return ai_config["ERROR_RESPONSE"]

    if response.status_code == 200:
        if image_data:
            try:
                result = response.json()
                return result.get("response", "").strip()[:ai_config["MAX_RESPONSE_LENGTH"]]
            except json.JSONDecodeError as e:
                print(f"json decode error: {e}")
                return ai_config["ERROR_RESPONSE"]
        else:
            full_response = ""
            try:
                for line in response.iter_lines():
                    if line:
                        chunk = line.decode("utf-8")
                        try:
                            json_chunk = json.loads(chunk)
                            full_response += json_chunk.get("response", "")
                            if json_chunk.get("done", False):
                                break
                        except json.JSONDecodeError:
                            print("JSON Decode Error:", chunk)
            finally:
                response.close()
            return full_response[:ai_config["MAX_RESPONSE_LENGTH"]]
    else:
        print(f"api error: {response.status_code}")
        return ai_config["ERROR_RESPONSE"]

async def process_image_for_ai(attachment):
    try:
        if not attachment.content_type or not attachment.content_type.startswith('image/'):
            return None
        if attachment.size > 10 * 1024 * 1024:
            return None

        image_data = await attachment.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')

        return base64_image
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def update_conversation_memory(channel_id, user_name, message_content, bot_response=None):
    """Update conversation memory for a channel"""
    if channel_id not in conversation_memory:
        conversation_memory[channel_id] = []

    # Add user message
    conversation_memory[channel_id].append(f"{user_name}: {message_content}")

    # Add bot response if provided
    if bot_response:
        conversation_memory[channel_id].append(f"{ai_config['BOT_NAME']}: {bot_response}")

    # Keep only last MAX_MEMORY_LENGTH messages
    if len(conversation_memory[channel_id]) > MAX_MEMORY_LENGTH * 2:  # *2 for user + bot messages
        conversation_memory[channel_id] = conversation_memory[channel_id][-(MAX_MEMORY_LENGTH * 2):]

def get_conversation_context(channel_id):
    """Get conversation context for a channel"""
    if channel_id not in conversation_memory:
        return ""
    return "\n".join(conversation_memory[channel_id])
