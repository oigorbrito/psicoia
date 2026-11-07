from typing import Any, Dict
import re


from ...core.base import EvaluationMethod
from ...utils import load_prompt
from jinja2 import Template
import json

from typing import List
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator  # Ensure ConfigDict is imported.

PANASItemName = Literal[
    "Interested",
    "Excited",
    "Strong",
    "Enthusiastic",
    "Proud",
    "Alert",
    "Inspired",
    "Determined",
    "Attentive",
    "Active",
    "Distressed",
    "Upset",
    "Guilty",
    "Scared",
    "Hostile",
    "Irritable",
    "Ashamed",
    "Nervous",
    "Jittery",
    "Afraid",
]

_PANAS_ORDER: list[str] = [
    "Interested",
    "Excited",
    "Strong",
    "Enthusiastic",
    "Proud",
    "Alert",
    "Inspired",
    "Determined",
    "Attentive",
    "Active",
    "Distressed",
    "Upset",
    "Guilty",
    "Scared",
    "Hostile",
    "Irritable",
    "Ashamed",
    "Nervous",
    "Jittery",
    "Afraid",
]


class Item(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    item: PANASItemName
    score: int = Field(ge=1, le=5)


class Items(BaseModel):  # Wrap the items in an object.
    model_config = ConfigDict(extra="forbid", strict=True)

    items: List[Item] = Field(min_length=20, max_length=20)

    @model_validator(mode="after")
    def _validate_order(self) -> "Items":
        names = [it.item for it in self.items]
        if names != _PANAS_ORDER:
            raise ValueError("PANAS items must be in the exact required order")
        return self

class PANAS(EvaluationMethod):

    def _parse_panas_response(self, data: list) -> float:
        """Parse a PANAS scale response."""
        # Convert the input list to a lookup dictionary for quick score access.
        # Keys are item names such as 'Interested' and 'Excited'; values are their scores.
        def _norm(s: str) -> str:
            return re.sub(r"\s+", "", str(s or "")).lower()

        data_lookup = {_norm(entry.get("item")): entry.get("score") for entry in data if isinstance(entry, dict)}
        
        scores = {}
        
        # Reference list of PANAS emotions.
        emotions = ['Interested', 'Excited', 'Strong', 'Enthusiastic', 'Proud', 'Alert', 'Inspired', 'Determined', 'Attentive', 'Active','Distressed', 'Upset', 'Guilty', 'Scared', 'Hostile', 'Irritable', 'Ashamed', 'Nervous', 'Jittery', 'Afraid']

        for emotion in emotions:
            # Retrieve the original score from the lookup dictionary.
            original_score = data_lookup.get(_norm(emotion))
            
            if original_score is not None:
                # Preserve the existing score calculation.
                # (original score - 1) * 2.5
                scores[f'panas_{emotion.lower()}'] = (original_score - 1) * 2.5


        # The following logic is retained from the original function.
        
        # Calculate positive and negative affect totals.
        # Keep the list fields unchanged.
        
        
        positive_emotions = ['interested', 'excited', 'strong', 'enthusiastic', 'proud', 'alert', 'inspired', 'determined', 'attentive', 'active'] 
        negative_emotions = ['distressed', 'upset', 'guilty', 'scared', 'hostile', 'irritable', 'ashamed', 'nervous', 'jittery','afraid']
        
        positive_total = sum(scores.get(f'panas_{emotion}', 0) for emotion in positive_emotions)
        negative_total = sum(scores.get(f'panas_{emotion}', 0) for emotion in negative_emotions)
        
        final_scores = {}
        
        num_positive = len(positive_emotions)
        num_negative = len(negative_emotions)

        final_scores['positive'] = positive_total / num_positive if num_positive > 0 else 0
        final_scores['negative'] = negative_total / num_negative if num_negative > 0 else 0
        
        # Keep the scoring method unchanged.
        final_score = (final_scores['positive'] - final_scores['negative'] + 10) / 2  # Convert to the 0–10 scale.
        
        return final_score

    async def evaluate(self, gpt_api, dialogue: Any, profile: dict = None) -> dict[str, float]:
        """Evaluate dialogue quality."""
        prompt = load_prompt("panas", "panas","cn")
        
        template = Template(prompt)
        prompt = template.render(intake_form=profile, diag=dialogue)

        # print(f"panas - panas prompt: {prompt}")

        messages=[{"role": "user", "content": prompt}]

        last_err: Exception | None = None
        for attempt in range(3):
            try:
                criteria_output = await self.chat_api(gpt_api, messages=messages)
                validated = Items.model_validate(json.loads(criteria_output))
                break
            except Exception as e:  # noqa: BLE001
                last_err = e
                if attempt >= 2:
                    raise
                messages = messages + [
                    {
                        "role": "user",
                        "content": "The previous output failed format validation. Return only one JSON object with the key `items`; `items` must contain exactly 20 entries in the required order. Each entry must contain only `item` (use the exact emotion label specified in the prompt) and `score` (an integer from 1 to 5).",
                    }
                ]
        else:  # pragma: no cover
            raise RuntimeError(f"Failed to get valid PANAS output: {last_err}")

        # 3. Convert the response list to the string format expected by the function.
        # Build a string such as "Interested: 2\nExcited: 1\n...".
        # score = {'items': [
        #     {'item': 'Interested', 'score': 2}, {'item': 'Excited', 'score': 1}, {'item': 'Strong', 'score': 3}, {'item': 'Enthusiastic', 'score': 2}, {'item': 'Proud', 'score': 3}, {'item': 'Alert', 'score': 2}, {'item': 'Inspired', 'score': 2}, {'item': 'Determined', 'score': 3}, {'item': 'Attentive', 'score': 3}, {'item': 'Active', 'score': 2}, 
        # {'item': 'Distressed', 'score': 4}, 
        # {'item': 'Upset', 'score': 4}, 
        # {'item': 'Guilty', 'score': 4}, 
        # {'item': 'Scared', 'score': 3}, 
        # {'item': 'Hostile', 'score': 2}, 
        # {'item': 'Irritable', 'score': 3}, 
        # {'item': 'Ashamed', 'score': 4}, 
        # {'item': 'Nervous', 'score': 4}, 
        # {'item': 'Jittery', 'score': 3}, 
        # {'item': 'Afraid', 'score': 4}]}
        final_score = self._parse_panas_response([it.model_dump() for it in validated.items])
        return {"client": final_score}


    def get_name(self) -> str:
        return "PANAS"
