from PIL import Image
from transformers import CLIPProcessor, CLIPModel


MODEL_NAME = "openai/clip-vit-base-patch32"


print("Loading AI image model...")

model = CLIPModel.from_pretrained(
    MODEL_NAME
)

processor = CLIPProcessor.from_pretrained(
    MODEL_NAME
)

print("AI image model loaded successfully.")


# =========================================================
# CIVIC IMAGE CATEGORIES
# =========================================================

CATEGORY_PROMPTS = {

    "Water Supply": [

        "a photo of water leakage",
        "a photo of a leaking water pipe",
        "a photo of a broken water pipeline",
        "a photo of water supply infrastructure damage",
        "a photo of a water pipe problem"

    ],

    "Electricity": [

        "a photo of a broken streetlight",
        "a photo of a streetlight that is not working",
        "a photo of an electric pole problem",
        "a photo of damaged electrical infrastructure",
        "a photo of an electrical civic problem"

    ],

    "Public Works": [

        "a photo of a pothole",
        "a photo of potholes on a road",
        "a photo of road damage",
        "a photo of a damaged road",
        "a photo of a broken road",
        "a photo of cracks on a road",
        "a photo of an uneven road",
        "a photo of road infrastructure damage"

    ]
}


# =========================================================
# NON-CIVIC PROMPTS
# =========================================================

NON_CIVIC_PROMPTS = [

    "a photo of an animal",
    "a photo of a person",
    "a photo of food",
    "a photo of a vehicle",
    "a photo of a house",
    "a photo of a building",
    "a photo of nature",
    "a photo of a landscape",
    "a photo of an unrelated object"
]


# =========================================================
# CLASSIFY IMAGE
# =========================================================

def classify_image(image_path):

    try:

        image = Image.open(
            image_path
        ).convert("RGB")


        # -------------------------------------------------
        # CREATE ALL PROMPTS
        # -------------------------------------------------

        labels = []

        label_categories = []


        for category, prompts in CATEGORY_PROMPTS.items():

            for prompt in prompts:

                labels.append(
                    prompt
                )

                label_categories.append(
                    category
                )


        for prompt in NON_CIVIC_PROMPTS:

            labels.append(
                prompt
            )

            label_categories.append(
                "Other"
            )


        # -------------------------------------------------
        # CLIP PROCESSING
        # -------------------------------------------------

        inputs = processor(
            text=labels,
            images=image,
            return_tensors="pt",
            padding=True
        )


        outputs = model(
            **inputs
        )


        probabilities = (
            outputs.logits_per_image[0]
            .softmax(dim=0)
        )


        # -------------------------------------------------
        # COLLECT CATEGORY SCORES
        # -------------------------------------------------

        category_scores = {

            "Water Supply": 0.0,

            "Electricity": 0.0,

            "Public Works": 0.0,

            "Other": 0.0
        }


        for index, category in enumerate(
            label_categories
        ):

            score = probabilities[
                index
            ].item()


            category_scores[
                category
            ] += score


        # -------------------------------------------------
        # PRINT SCORES
        # -------------------------------------------------

        print(
            "Category Scores:"
        )


        for category, score in category_scores.items():

            print(
                f"{category}: {score:.4f}"
            )


        # -------------------------------------------------
        # BEST CATEGORY
        # -------------------------------------------------

        best_category = max(
            category_scores,
            key=category_scores.get
        )


        best_score = category_scores[
            best_category
        ]


        print(
            "Best Image Category:",
            best_category
        )


        print(
            "Best Image Score:",
            best_score
        )


        # =================================================
        # REJECT NON-CIVIC IMAGES
        # =================================================

        CIVIC_CATEGORIES = [
            "Water Supply",
            "Electricity",
            "Public Works"
        ]


        if best_category not in CIVIC_CATEGORIES:

            print(
                "Image rejected: "
                "non-civic image"
            )

            return {

                "classification": "Other",

                "confidence": 0,

                "label": (
                    "Non-civic image"
                ),

                "is_civic": False
            }


        # -------------------------------------------------
        # MINIMUM CIVIC SCORE
        # -------------------------------------------------

        MIN_CIVIC_SCORE = 0.20


        if best_score < MIN_CIVIC_SCORE:

            print(
                "Image rejected: "
                "low civic confidence"
            )

            return {

                "classification": "Other",

                "confidence": 0,

                "label": (
                    "Unclear civic image"
                ),

                "is_civic": False
            }


        # =================================================
        # ACCEPT CIVIC IMAGE
        # =================================================

        print(
            "Image accepted as:",
            best_category
        )


        return {

            "classification": best_category,

            "confidence": round(
                best_score,
                4
            ),

            "label": (
                best_category
                + " civic problem"
            ),

            "is_civic": True
        }


    except Exception as e:

        print(
            "Image classification error:",
            e
        )


        return {

            "classification": "Other",

            "confidence": 0,

            "label": (
                "Unable to classify image"
            ),

            "is_civic": False
        }