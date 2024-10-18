import hashlib
import streamlit as st

print("Defining function assign_ids")

def assign_hash_to_dictionary(worldviews):
    id_counter = 1
    statement_dict = {}
    
    for worldview, types in worldviews.items():
        for category, statements in types.items():
            for statement in statements:
                # hash statement to create unique ID
                statement_hash = hashlib.md5(statement.encode()).hexdigest()
                statement_dict[id_counter] = {
                    "worldview": worldview,
                    "category": category,
                    "statement": statement,
                    "hash": statement_hash
                }
                id_counter += 1
    return statement_dict



worldviews = {
    "Mechanical": {
        "in_accord": [
            "The universe operates like a precise clockwork mechanism, following fixed, predictable laws.",
            "Human progress is achieved through mastering and controlling nature via technology.",
            "Success is measured by efficiency and productivity, with everything in its rightful place.",
            "Order and predictability are essential for a stable society, and disruption is to be minimised.",
            "The individual's role is to fit into pre-defined systems, optimising their function within it."
        ],
        "in_disaccord": [
            "Life is spontaneous and cannot be reduced to predictable formulas or systems.",
            "Human beings should focus on emotional and spiritual growth rather than control and efficiency.",
            "The natural world is too complex and interconnected to be treated as a mere machine."
        ]
    },
    
    "Organic": {
        "in_accord": [
            "All beings and elements of nature are interconnected in a web of life.",
            "Growth and evolution occur naturally through balance and adaptation, not control.",
            "Humans are part of a larger living system and must respect nature's cycles and rhythms.",
            "Diversity in ecosystems and societies fosters resilience and strength.",
            "Healing and well-being come from harmony and alignment with natural forces."
        ],
        "in_disaccord": [
            "Nature is something to be mastered, controlled, and manipulated for human benefit.",
            "The world can be fully understood and managed by breaking it down into separate, independent parts.",
            "Human progress is measured only by technological advancements and resource exploitation."
        ]
    },
    
    "Dramatic/Playful": {
        "in_accord": [
            "Life is a creative expression where spontaneity and improvisation are valued.",
            "Every individual plays a unique role in the cosmic drama, contributing to the collective story.",
            "Mistakes and failures are simply part of the playful unfolding of life, not to be feared.",
            "The world is a stage, and human existence is filled with opportunities for personal expression and creativity.",
            "Reality is flexible, open to interpretation, and subject to change based on the play of ideas."
        ],
        "in_disaccord": [
            "Life must follow strict rules, and spontaneity should be suppressed in favor of order and control.",
            "The world is a machine with no room for creativity or improvisation.",
            "Success is about efficiency and productivity, not playfulness and joy."
        ]
    },
    
    "Animistic": {
        "in_accord": [
            "Everything in nature, from animals to rivers, possesses a spiritual essence and is interconnected.",
            "Humans must live in harmony with the natural world and respect its spiritual forces.",
            "Rituals and offerings are vital for maintaining balance between the human and spiritual realms.",
            "The Earth is a living being, and its well-being is inseparable from our own.",
            "Knowledge comes from deep, direct experience with nature and the spirit world, not from abstract reasoning."
        ],
        "in_disaccord": [
            "Nature is devoid of spirit and exists solely for human exploitation and control.",
            "Progress is measured by the extraction of natural resources without regard for environmental consequences.",
            "Humans are superior to other living beings and should dominate the natural world."
        ]
    },
    
    "Ubuntu": {
        "in_accord": [
            '"I am because we are" – Human beings are fundamentally interconnected and interdependent.',
            "Collective well-being is more important than individual success, and compassion guides decision-making.",
            "Shared responsibility and mutual support are key to a thriving community.",
            "Dignity and respect must be afforded to all members of the community, regardless of their differences.",
            "Humanity is enriched through cooperation, generosity, and a sense of belonging to the collective."
        ],
        "in_disaccord": [
            "Individualism and self-interest should guide actions, with little regard for the community.",
            "Success is measured by individual wealth and status, rather than shared prosperity.",
            "The needs of the collective are secondary to personal ambition and competition."
        ]
    }
}
    # Function to display choices


if __name__ == "__main__":
    statement_dict = assign_hash_to_dictionary(worldviews)
    st.write(statement_dict)