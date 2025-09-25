from transformers import Owlv2Processor, Owlv2ForObjectDetection
from PIL import Image, ImageDraw
import torch

# Load model once
processor = Owlv2Processor.from_pretrained("google/owlv2-base-patch16")
model = Owlv2ForObjectDetection.from_pretrained("google/owlv2-base-patch16")


def detect_element(image_path, query="cart icon", score_threshold=0.2, debug_output="vision_debug.png"):
    """
    Use OWL-ViT to detect UI element by natural language query.
    Returns element-like dict with 'bounds'.
    Also saves an image with the bounding box drawn for debugging.
    """
    image = Image.open(image_path).convert("RGB")
    inputs = processor(text=[[query]], images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes)

    boxes, scores, labels = results[0]["boxes"], results[0]["scores"], results[0]["labels"]

    draw = ImageDraw.Draw(image)
    chosen = None

    for box, score, label in zip(boxes, scores, labels):
        if score > score_threshold:
            x1, y1, x2, y2 = map(int, box.tolist())
            bounds_str = f"[{x1},{y1}][{x2},{y2}]"
            chosen = {
                "text": query,
                "resource_id": "",
                "bounds": bounds_str
            }
            # Draw bounding box
            draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
            draw.text((x1, y1 - 10), f"{query} ({score:.2f})", fill="red")
            break  # only first match

    # Save debug image
    image.save(debug_output)

    return chosen
