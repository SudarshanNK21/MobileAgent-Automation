from transformers import Owlv2Processor, Owlv2ForObjectDetection
from PIL import Image
import torch

# Load model once
processor = Owlv2Processor.from_pretrained("google/owlv2-base-patch16")
model = Owlv2ForObjectDetection.from_pretrained("google/owlv2-base-patch16")

def detect_element(image_path, query="cart icon", score_threshold=0.2):
    """
    Use OWL-ViT to detect UI element by natural language query.
    Returns bounding box (x1, y1, x2, y2) if found.
    """
    image = Image.open(image_path).convert("RGB")
    inputs = processor(text=[[query]], images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes)

    boxes, scores, labels = results[0]["boxes"], results[0]["scores"], results[0]["labels"]

    for box, score, label in zip(boxes, scores, labels):
        if score > score_threshold:
            x1, y1, x2, y2 = box.tolist()
            return (int(x1), int(y1), int(x2), int(y2))

    return None
