from src.agent.llava_query import test_llava_inference

if __name__ == "__main__":
    # Path to the image you want to test
    image_path = "vision_test.png"  # Change if needed
    query = "Describe the main object."
    
    print(f"Sending image '{image_path}' to Llava with query: '{query}'...")
    result = test_llava_inference(image_path, query)
    print("Llava result:", result)
    