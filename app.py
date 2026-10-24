from dataclasses import asdict
from datetime import date
import json
from ai_service import generate_text
from flask import Flask, jsonify, render_template, request

from numerology_system import (
    build_multi_tradition_person,
    evaluate_global_compatibility,
    format_multi_tradition_individual,
    format_global_compatibility_report,
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024


@app.get("/")
def index():
    return render_template("index.html")


def build_person(data):
    if not isinstance(data, dict):
        raise ValueError("Person details must be an object.")

    first = data.get("first_name")
    last = data.get("last_name")
    gender = data.get("gender")

    if not isinstance(first, str) or not isinstance(last, str):
        raise ValueError("Enter first and last names.")

    if not first.strip() or not last.strip():
        raise ValueError("Enter first and last names.")

    if len(first) > 100 or len(last) > 100:
        raise ValueError("Names must be 100 characters or fewer.")

    if gender not in ("Male", "Female", "Non-Binary"):
        raise ValueError("Select a valid gender.")

    parts = []
    for field in ("birth_year", "birth_month", "birth_day"):
        value = data.get(field)
        if type(value) is not int:
            raise ValueError("Birth date values must be whole numbers.")
        parts.append(value)

    birthday = date(*parts)

    if birthday > date.today():
        raise ValueError("Birth date cannot be in the future.")

    return build_multi_tradition_person(
        first.strip(), last.strip(), *parts, gender
    )


@app.post("/api/reading")
def reading():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(error="Send a JSON object."), 400

    try:
        mode = data.get("mode", "individual")

        if mode not in ("individual", "couple"):
            raise ValueError("Select individual or couple mode.")

        person1 = build_person(data.get("person1"))

        if mode == "couple":
            person2 = build_person(data.get("person2"))
            result = evaluate_global_compatibility(person1, person2)
            report = format_global_compatibility_report(result)
        else:
            result = person1
            report = format_multi_tradition_individual(person1)

        try:
            # Send calculated symbols, without names or full birth dates.
            def symbols(person):
                return {
                    key: value for key, value in asdict(person).items()
                    if key not in {"first_name", "last_name", "birth_year",
                                   "birth_month", "birth_day", "gender", "polarity"}
                }

            context = {"mode": mode, "person1": symbols(person1)}
            if mode == "couple":
                context["person2"] = symbols(person2)

            raw = generate_text(
                'Return ONLY a valid JSON object with exactly three string keys: '
                '"partner", "friend", "colleague". Each value must be a short '
                'personalised paragraph of 25-35 words, with one practical '
                'reflection based on the supplied numerology and zodiac symbols. '
                'For individual mode describe the person in each role; for couple '
                'mode describe how the two people may relate in each role. '
                'Treat symbols as entertainment and reflection, not factual '
                'predictions. Do not invent or change numbers, give scores, or '
                'infer traits from gender. No markdown fences or HTML. '
                'Keep the entire JSON response under 150 words. Data:\n'
                + json.dumps(context, ensure_ascii=False)
            )
            # Some models wrap JSON in a markdown fence despite instructions.
            raw = raw.strip()
            if raw.startswith("```") and raw.endswith("```"):
                raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            interpretations = json.loads(raw)
            roles = ("partner", "friend", "colleague")
            if not isinstance(interpretations, dict) or any(
                not isinstance(interpretations.get(role), str)
                or not interpretations[role].strip()
                or len(interpretations[role]) > 2000
                for role in roles
            ):
                raise ValueError("Invalid generated interpretation format.")
            interpretations = {
                role: interpretations[role].strip() for role in roles
            }
        except Exception:
            app.logger.exception("AI reading failed")
            return jsonify(
                error="The AI service is unavailable. Please try again."
            ), 502

        return jsonify(
            mode=mode,
            result=asdict(result),
            interpretations=interpretations,
        )

    except (ValueError, TypeError) as error:
        return jsonify(error=str(error)), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)