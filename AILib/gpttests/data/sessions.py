# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# The standard conversation sessions of the model data tests: 20 turns in 8 sessions, 10 factual and 10 creative.
#
# Factual (10): capital of France (1 turn), author of Frankenstein (1), Apollo 11 (3), William Shakespeare (5).
# Creative (10): short story + reaction (2), a poem (1), a sensory description (1), a six-turn story written around a given character (6).
#
# Each turn: prompt + Tier A rules (must_any / must_all / must_not / regex, checked without any judge) + reference facts (ground truth
# for the NLI verifier and the LLM judge) + a judge rubric. Keep every fact atomic (one claim per sentence): the NLI cross-encoder scores
# each response sentence against each fact, and compound facts produce false contradictions for sentences about only one half.
#
# Design notes (measured on andres-350M-1 / andres-350M-1-fp8 before these were chosen):
# - Shakespeare is a topic the models usually get right (19/20 and 13/20 turn samples) but not always: the birth town and the Globe are
#   the discriminating turns. Einstein (both models call E = mc^2 "the theory of relativity") and the Amazon (Brasilia, rambling) were worse fits.
# - Creative prompts are phrased as direct writing instructions. "Let's write a story together, invent a character..." made the fp8 model
#   refuse every turn ("I am an AI language model and do not have the ability to create characters") and "using the five senses" triggered
#   "as an AI I cannot see"; giving the character in the prompt lets every later turn require the names, i.e. test multi-turn consistency.
# - Prompts contain a creative keyword (write / story / poem / describe...) so validators.validate_format_quality applies its creative
#   rules (no verbosity limit, story length check) rather than the factual ones.

from typing import Any, Dict, List

from gpttests.data.validators import (
    CATEGORY_CREATIVE, SPEC_CATEGORY, SPEC_FACTS, SPEC_MUST_ALL, SPEC_MUST_ANY, SPEC_MUST_NOT, SPEC_PROMPT, SPEC_REGEX, SPEC_RUBRIC,
)

TEST_SESSIONS: List[List[Dict[str, Any]]] = [
    # ---------------------------------------------------------------- factual: 1 + 1 + 3 + 5 turns
    [
        {
            SPEC_PROMPT: "what is the capital of france?",
            SPEC_MUST_ANY: ["Paris"],
            SPEC_FACTS: ["Paris is the capital of France."],
        },
    ],
    [
        {
            SPEC_PROMPT: 'who wrote the book "frankenstein"?',
            SPEC_MUST_ANY: ["Mary Shelley", "Shelley"],
            SPEC_MUST_NOT: ["Chronicles"],
            SPEC_FACTS: [
                "Frankenstein was written by Mary Shelley.",
                "Mary Shelley was an English author.",
                "Frankenstein was first published in 1818.",
                "Victor Frankenstein is the scientist who creates the creature.",
                "The creature in Frankenstein has no name.",
                "Frankenstein is a Gothic novel.",
                "Frankenstein is often regarded as the first science fiction novel.",
            ],
        },
    ],
    [
        {
            SPEC_PROMPT: "when did mankind first land on the moon?",
            SPEC_MUST_ANY: ["1969"],
            SPEC_FACTS: [
                "Apollo 11 landed the first humans on the Moon on July 20, 1969.",
                "Neil Armstrong and Buzz Aldrin were the first humans to walk on the Moon.",
                "Apollo 11 launched on July 16, 1969.",
                "Apollo 11 launched from the Kennedy Space Center in Florida.",
                "Apollo 11 landed in the Sea of Tranquility.",
                "Neil Armstrong said 'That's one small step for man, one giant leap for mankind' when he stepped onto the Moon.",
            ],
        },
        {
            SPEC_PROMPT: "what was the name of the rocket that took them there?",
            SPEC_MUST_ANY: ["Saturn V"],
            SPEC_FACTS: [
                "The Saturn V rocket launched the Apollo 11 astronauts to the Moon.",
                "The Saturn V was developed by NASA.",
                "The Saturn V was designed at the Marshall Space Flight Center in Huntsville, Alabama, under Wernher von Braun.",
                "The Saturn V is the most powerful rocket ever flown successfully.",
            ],
        },
        {
            SPEC_PROMPT: "in what country was the rocket made?",
            SPEC_MUST_ANY: ["United States", "USA", "U.S.", "America"],
            SPEC_FACTS: [
                "The Saturn V rocket was designed and built in the United States of America.",
                "Huntsville, Alabama is in the United States.",
                "The Kennedy Space Center in Florida is in the United States.",
                "NASA is the space agency of the United States government.",
                "Saturn V stages were built by Boeing, North American Aviation and Douglas Aircraft in the United States.",
            ],
        },
    ],
    [
        {
            SPEC_PROMPT: "who wrote the play romeo and juliet?",
            SPEC_MUST_ANY: ["Shakespeare"],
            SPEC_FACTS: [
                "Romeo and Juliet was written by William Shakespeare.",
                "Romeo and Juliet is a tragedy.",
                "Romeo and Juliet was written in the 1590s.",
                "Romeo and Juliet is set in Verona, Italy.",
                "Romeo and Juliet are young lovers from the feuding Montague and Capulet families.",
            ],
        },
        {
            SPEC_PROMPT: "in which country was he born?",
            SPEC_MUST_ANY: ["England", "English", "Britain", "United Kingdom"],
            SPEC_FACTS: [
                "William Shakespeare was born in England.",
                "William Shakespeare was born in 1564.",
                "William Shakespeare died in 1616.",
                "William Shakespeare was an English playwright and poet.",
            ],
        },
        {
            SPEC_PROMPT: "in which town was he born?",
            SPEC_MUST_ANY: ["Stratford"],
            SPEC_FACTS: [
                "William Shakespeare was born in Stratford-upon-Avon.",
                "Stratford-upon-Avon is a town in Warwickshire, England.",
                "William Shakespeare was baptised on April 26, 1564.",
                "William Shakespeare's wife was Anne Hathaway.",
                "William Shakespeare died in Stratford-upon-Avon in 1616.",
            ],
        },
        {
            SPEC_PROMPT: "what was the name of the famous theatre in london where his plays were performed?",
            SPEC_MUST_ANY: ["Globe"],
            SPEC_FACTS: [
                "The Globe Theatre in London is the theatre most associated with Shakespeare's plays.",
                "The Globe Theatre was built in 1599.",
                "The Globe Theatre was built by Shakespeare's playing company, the Lord Chamberlain's Men.",
                "The Globe Theatre stood on the south bank of the River Thames.",
                "The original Globe Theatre burned down in 1613.",
                "A reconstruction called Shakespeare's Globe opened in London in 1997.",
            ],
        },
        {
            SPEC_PROMPT: "name another famous tragedy he wrote.",
            SPEC_MUST_ANY: ["Hamlet", "Macbeth", "Othello", "King Lear", "Julius Caesar", "Antony and Cleopatra", "Coriolanus", "Titus Andronicus"],
            SPEC_FACTS: [
                "Hamlet is a tragedy by William Shakespeare.",
                "Macbeth is a tragedy by William Shakespeare.",
                "Othello is a tragedy by William Shakespeare.",
                "King Lear is a tragedy by William Shakespeare.",
                "Julius Caesar is a tragedy by William Shakespeare.",
                "Hamlet is set in Denmark.",
                "Macbeth is set in Scotland.",
                "A Midsummer Night's Dream is a comedy by William Shakespeare, not a tragedy.",
            ],
            SPEC_RUBRIC: "The answer must name a Shakespeare tragedy other than Romeo and Juliet. Naming a comedy or history play, or a work by another author, is a failure.",
        },
    ],
    # ---------------------------------------------------------------- creative: 2 + 1 + 1 + 6 turns
    [
        {
            SPEC_PROMPT: "please write a short story",
            SPEC_CATEGORY: CATEGORY_CREATIVE,
            SPEC_RUBRIC: "Must be a complete short story with a beginning, middle and end, a consistent protagonist (same name throughout), and no restarts or repeated passages.",
        },
        {
            SPEC_PROMPT: "how does this story make you feel?",
            SPEC_CATEGORY: CATEGORY_CREATIVE,
            SPEC_RUBRIC: "Must describe the assistant's own reaction or feelings about the story from the previous turn and refer to specific elements of that story (characters, events, themes). It must not be a new story and must not describe a different story.",
        },
    ],
    [
        {
            SPEC_PROMPT: "write a short poem about the ocean",
            SPEC_CATEGORY: CATEGORY_CREATIVE,
            SPEC_MUST_ANY: ["ocean", "sea", "wave", "tide", "shore"],
            SPEC_RUBRIC: "Must be a poem about the ocean or the sea: written in verse (short lines or stanzas) with some imagery. It does not need to rhyme. A prose paragraph, an essay about oceans, or a poem about an unrelated subject is a failure.",
        },
    ],
    [
        {
            SPEC_PROMPT: "write one paragraph describing a busy morning market: what people see, hear and smell there.",
            SPEC_CATEGORY: CATEGORY_CREATIVE,
            SPEC_MUST_ANY: ["market"],
            SPEC_RUBRIC: "Must be a vivid description of a market in the morning that covers at least two of the three senses asked for (sight, sound, smell). A definition of what a market is, a list of bullet points, or a refusal ('as an AI I cannot see') is a failure.",
        },
    ],
    [
        {
            SPEC_PROMPT: "start a story about Maya, a 34-year-old baker who lives in a small town by the sea. write only the first paragraph, introducing her and her bakery.",
            SPEC_CATEGORY: CATEGORY_CREATIVE,
            SPEC_MUST_ALL: ["Maya"],
            SPEC_MUST_ANY: ["baker", "bakery", "bread", "pastr", "loaves"],
            SPEC_RUBRIC: "Must be the opening of a story that introduces Maya as a baker in a small seaside town. Changing her name, age or job, or writing a whole story with an ending, is a failure.",
        },
        {
            SPEC_PROMPT: "continue the story: one morning maya finds a mysterious old key in a sack of flour. write that paragraph.",
            SPEC_CATEGORY: CATEGORY_CREATIVE,
            SPEC_MUST_ALL: ["Maya", "key"],
            SPEC_RUBRIC: "Must continue the same story: Maya finds an old key in a sack of flour. Restarting the story, forgetting that she is a baker, or not mentioning the key is a failure.",
        },
        {
            SPEC_PROMPT: "now write a short conversation in which maya shows the key to her friend tom, who thinks she should keep it a secret.",
            SPEC_CATEGORY: CATEGORY_CREATIVE,
            SPEC_MUST_ALL: ["Maya", "Tom", "key"],
            SPEC_REGEX: r'["\u201c]|(^|\n)\s*(Maya|Tom)\s*:',
            SPEC_RUBRIC: "Must be a dialogue between Maya and Tom (quoted speech or a script with their names) about the key, in which Tom argues for keeping it secret. Both names must be used consistently.",
        },
        {
            SPEC_PROMPT: "write one paragraph describing the old lighthouse at the edge of town. maya thinks the key might belong to it.",
            SPEC_CATEGORY: CATEGORY_CREATIVE,
            SPEC_MUST_ALL: ["lighthouse"],
            SPEC_RUBRIC: "Must describe an old lighthouse at the edge of Maya's seaside town, consistent with the story so far, and connect it to the key. A description of a different building or an unrelated place is a failure.",
        },
        {
            SPEC_PROMPT: "write the ending of the story: maya finally discovers what the key opens.",
            SPEC_CATEGORY: CATEGORY_CREATIVE,
            SPEC_MUST_ALL: ["Maya", "key"],
            SPEC_RUBRIC: "Must end the same story: Maya discovers what the key opens (a door, box, room, chest...). The ending must be consistent with the earlier turns (her name, the bakery, the key, the lighthouse) and must not restart the story.",
        },
        {
            SPEC_PROMPT: "suggest a title for this story and explain in one sentence why it fits.",
            SPEC_CATEGORY: CATEGORY_CREATIVE,
            SPEC_RUBRIC: "Must propose a title that fits the story about Maya, the key and the lighthouse, followed by a one-sentence justification that refers to the story. A title for a different story, or a new story instead of a title, is a failure.",
        },
    ],
]


def _q(prompt: str, must_any: List[str], facts: List[str], must_not: List[str] = None, regex: str = None) -> Dict[str, Any]:
    """A single-turn factual spec. Accepted answers are checked as case-insensitive substrings, so short symbols/numbers go in regex instead."""
    spec: Dict[str, Any] = {SPEC_PROMPT: prompt, SPEC_FACTS: facts}
    if must_any:
        spec[SPEC_MUST_ANY] = must_any
    if must_not:
        spec[SPEC_MUST_NOT] = must_not
    if regex:
        spec[SPEC_REGEX] = regex
    return spec


# Extended factual set (opt-in with --extended_factual): ~100 further factual turns so that factual accuracy is measured on hundreds of
# distinct questions rather than ten. Single-turn questions across geography, science, history and the arts at the difficulty of the
# standard set, plus five three-turn threads whose follow-ups rely on a pronoun ("he", "it", "she") to test whether the model keeps the referent.
FACTUAL_SESSIONS_EXTENDED: List[List[Dict[str, Any]]] = [[s] for s in [
    # geography
    _q("what is the capital of japan?", ["Tokyo"], ["Tokyo is the capital of Japan."]),
    _q("what is the capital of canada?", ["Ottawa"], ["Ottawa is the capital of Canada.", "Toronto is the largest city in Canada but not its capital."], must_not=["Toronto"]),
    _q("what is the capital of australia?", ["Canberra"], ["Canberra is the capital of Australia.", "Sydney is the largest city in Australia but not its capital."], must_not=["Sydney"]),
    _q("what is the capital of germany?", ["Berlin"], ["Berlin is the capital of Germany."]),
    _q("what is the capital of italy?", ["Rome"], ["Rome is the capital of Italy."]),
    _q("what is the capital of spain?", ["Madrid"], ["Madrid is the capital of Spain."]),
    _q("what is the capital of egypt?", ["Cairo"], ["Cairo is the capital of Egypt."]),
    _q("what is the capital of brazil?", ["Brasilia", "Brasília"], ["Brasilia is the capital of Brazil.", "Rio de Janeiro was the capital of Brazil until 1960."], must_not=["Rio"]),
    _q("what is the capital of russia?", ["Moscow"], ["Moscow is the capital of Russia."]),
    _q("what is the capital of china?", ["Beijing"], ["Beijing is the capital of China."]),
    _q("what is the capital of india?", ["Delhi"], ["New Delhi is the capital of India."]),
    _q("what is the capital of mexico?", ["Mexico City"], ["Mexico City is the capital of Mexico."]),
    _q("what is the capital of the united kingdom?", ["London"], ["London is the capital of the United Kingdom."]),
    _q("what is the capital of south korea?", ["Seoul"], ["Seoul is the capital of South Korea."]),
    _q("what is the largest ocean on earth?", ["Pacific"], ["The Pacific Ocean is the largest ocean on Earth."]),
    _q("what is the longest river in africa?", ["Nile"], ["The Nile is the longest river in Africa.", "The Nile flows north into the Mediterranean Sea."]),
    _q("what is the longest river in south america?", ["Amazon"], ["The Amazon is the longest river in South America.", "The Amazon carries more water than any other river."]),
    _q("what is the largest hot desert in the world?", ["Sahara"], ["The Sahara is the largest hot desert in the world.", "The Sahara is in northern Africa."]),
    _q("on which continent is egypt?", ["Africa"], ["Egypt is in Africa.", "The Sinai Peninsula of Egypt is in Asia."]),
    _q("what is the largest country in the world by area?", ["Russia"], ["Russia is the largest country in the world by area."]),
    _q("what is the largest continent?", ["Asia"], ["Asia is the largest continent."]),
    _q("what is the smallest continent?", ["Australia", "Oceania"], ["Australia is the smallest continent."]),
    _q("what is the largest island in the world?", ["Greenland"], ["Greenland is the largest island in the world.", "Australia is considered a continent rather than an island."]),
    _q("what language is spoken in brazil?", ["Portuguese"], ["Portuguese is the official language of Brazil."]),
    _q("what language is spoken in argentina?", ["Spanish"], ["Spanish is the official language of Argentina."]),
    _q("what is the main language spoken in mexico?", ["Spanish"], ["Spanish is the most spoken language in Mexico."]),
    _q("what is the main language spoken in china?", ["Mandarin", "Chinese"], ["Mandarin Chinese is the most spoken language in China."]),
    _q("what currency is used in japan?", ["yen"], ["The yen is the currency of Japan."]),
    _q("what currency is used in the united kingdom?", ["pound"], ["The pound sterling is the currency of the United Kingdom."]),
    _q("in which country is the city of venice?", ["Italy"], ["Venice is a city in Italy."]),
    _q("in which city is the eiffel tower?", ["Paris"], ["The Eiffel Tower is in Paris, France.", "The Eiffel Tower was completed in 1889."]),
    _q("in which city is the colosseum?", ["Rome"], ["The Colosseum is in Rome, Italy."]),
    _q("in which country are the pyramids of giza?", ["Egypt"], ["The pyramids of Giza are in Egypt."]),
    _q("in which country is mount fuji?", ["Japan"], ["Mount Fuji is in Japan.", "Mount Fuji is the highest mountain in Japan."]),
    _q("which country gave the statue of liberty to the united states?", ["France", "French"], ["France gave the Statue of Liberty to the United States.", "The Statue of Liberty was dedicated in 1886."]),
    _q("what is the largest city in the united states?", ["New York"], ["New York City is the largest city in the United States by population."]),
    _q("on which continent is the amazon rainforest?", ["South America"], ["The Amazon rainforest is in South America.", "Most of the Amazon rainforest is in Brazil."]),
    _q("what is the longest wall in the world?", ["Great Wall"], ["The Great Wall of China is the longest wall in the world."]),
    # science and nature
    _q("what is the smallest planet in our solar system?", ["Mercury"], ["Mercury is the smallest planet in the solar system.", "Pluto is classified as a dwarf planet."], must_not=["Pluto"]),
    _q("which planet is closest to the sun?", ["Mercury"], ["Mercury is the planet closest to the Sun."]),
    _q("which planet is known as the red planet?", ["Mars"], ["Mars is known as the Red Planet."]),
    _q("what is the closest star to earth?", ["Sun"], ["The Sun is the closest star to Earth.", "Proxima Centauri is the closest star to the Sun."]),
    _q("how many planets are there in our solar system?", ["eight", " 8 ", " 8.", " 8,"], ["There are eight planets in the solar system."]),
    _q("what is the chemical symbol for gold?", [], ["The chemical symbol for gold is Au."], regex=r"\bAu\b"),
    _q("what is the chemical formula of water?", [], ["The chemical formula of water is H2O.", "A water molecule has two hydrogen atoms and one oxygen atom."], regex=r"H2O|H₂O"),
    _q("what gas do plants take in from the air to make food?", ["carbon dioxide", "CO2", "CO₂"], ["Plants take in carbon dioxide for photosynthesis.", "Plants release oxygen during photosynthesis."]),
    _q("what gas do humans need to breathe to survive?", ["oxygen"], ["Humans need oxygen to survive."]),
    _q("what is the process by which plants make food using sunlight called?", ["photosynthesis"], ["Photosynthesis is the process by which plants make food using sunlight."]),
    _q("at what temperature does water boil in celsius?", ["100"], ["Water boils at 100 degrees Celsius at sea level."]),
    _q("at what temperature does water freeze in celsius?", ["zero", "0 degrees", "0°", "0 °", "0 celsius", "0C"], ["Water freezes at 0 degrees Celsius."]),
    _q("how many legs does a spider have?", ["eight", " 8 ", " 8.", " 8,"], ["Spiders have eight legs.", "Insects have six legs."]),
    _q("what is the largest mammal in the world?", ["blue whale"], ["The blue whale is the largest mammal in the world.", "The blue whale is the largest animal ever known to have lived."]),
    _q("what is the largest animal that lives on land?", ["elephant"], ["The African elephant is the largest land animal."]),
    _q("what is the fastest land animal?", ["cheetah"], ["The cheetah is the fastest land animal."]),
    _q("what is the largest bird in the world?", ["ostrich"], ["The ostrich is the largest bird in the world.", "The ostrich cannot fly."]),
    _q("what is the hardest natural substance?", ["diamond"], ["Diamond is the hardest natural substance."]),
    _q("which organ pumps blood through the human body?", ["heart"], ["The heart pumps blood through the body."]),
    _q("what is the largest organ of the human body?", ["skin"], ["The skin is the largest organ of the human body."]),
    _q("how many bones does an adult human have?", ["206"], ["An adult human has 206 bones."]),
    _q("what is the center of an atom called?", ["nucleus"], ["The center of an atom is called the nucleus.", "The nucleus contains protons and neutrons."]),
    _q("what force pulls objects toward the earth?", ["gravity"], ["Gravity pulls objects toward the Earth."]),
    _q("what do bees make?", ["honey"], ["Bees make honey from nectar.", "Bees also make beeswax."]),
    _q("what animal is called the king of the jungle?", ["lion"], ["The lion is called the king of the jungle."]),
    _q("roughly how fast does light travel?", ["300,000", "300000", "186,000", "186000", "299,792", "299792", "3 x 10", "3×10", "3e8"], ["Light travels at about 300,000 kilometres per second.", "Light travels at about 186,000 miles per second."]),
    # history and people
    _q("who developed the theory of relativity?", ["Einstein"], ["Albert Einstein developed the theory of relativity."]),
    _q("who discovered penicillin?", ["Fleming"], ["Alexander Fleming discovered penicillin.", "Penicillin was discovered in 1928."]),
    _q("who is credited with inventing the telephone?", ["Bell"], ["Alexander Graham Bell is credited with inventing the telephone.", "Bell patented the telephone in 1876."]),
    _q("who formulated the laws of motion and universal gravitation?", ["Newton"], ["Isaac Newton formulated the laws of motion and universal gravitation."]),
    _q("who developed the first polio vaccine?", ["Salk", "Sabin"], ["Jonas Salk developed the first effective polio vaccine.", "Albert Sabin developed the oral polio vaccine."]),
    _q("who was the first woman to win a nobel prize?", ["Curie"], ["Marie Curie was the first woman to win a Nobel Prize.", "Marie Curie won the Nobel Prize in Physics in 1903."]),
    _q("who painted the ceiling of the sistine chapel?", ["Michelangelo"], ["Michelangelo painted the ceiling of the Sistine Chapel.", "The Sistine Chapel ceiling was painted between 1508 and 1512."]),
    _q("who painted the starry night?", ["Gogh"], ["Vincent van Gogh painted The Starry Night.", "The Starry Night was painted in 1889."]),
    _q("who composed the ninth symphony that includes the ode to joy?", ["Beethoven"], ["Ludwig van Beethoven composed the Ninth Symphony.", "The Ode to Joy is in the final movement of Beethoven's Ninth Symphony."]),
    _q("who wrote the play hamlet?", ["Shakespeare"], ["William Shakespeare wrote Hamlet."]),
    _q("who wrote the odyssey?", ["Homer"], ["The Odyssey is attributed to Homer.", "The Odyssey is an ancient Greek epic poem."]),
    _q("who wrote the novel 1984?", ["Orwell"], ["George Orwell wrote 1984.", "1984 was published in 1949."]),
    _q("who wrote the harry potter books?", ["Rowling"], ["J. K. Rowling wrote the Harry Potter books."]),
    _q("who wrote don quixote?", ["Cervantes"], ["Miguel de Cervantes wrote Don Quixote.", "Don Quixote is a Spanish novel."]),
    _q("who wrote on the origin of species?", ["Darwin"], ["Charles Darwin wrote On the Origin of Species.", "On the Origin of Species was published in 1859."]),
    _q("what was the name of the ship charles darwin sailed on?", ["Beagle"], ["Charles Darwin sailed on HMS Beagle."]),
    _q("which ancient greek philosopher was the teacher of alexander the great?", ["Aristotle"], ["Aristotle was the tutor of Alexander the Great."]),
    _q("julius caesar was a leader of which ancient civilization?", ["Rome", "Roman"], ["Julius Caesar was a Roman general and statesman."]),
    _q("which ancient civilization built the pyramids of giza?", ["Egypt"], ["The ancient Egyptians built the pyramids of Giza."]),
    _q("who was the first president of the united states?", ["Washington"], ["George Washington was the first president of the United States."]),
    _q("who was the president of the united states during the civil war?", ["Lincoln"], ["Abraham Lincoln was the president of the United States during the Civil War."]),
    _q("who was the first person to travel into space?", ["Gagarin"], ["Yuri Gagarin was the first person to travel into space.", "Gagarin's flight took place in 1961."]),
    _q("in what year did world war ii end?", ["1945"], ["World War II ended in 1945."]),
    _q("in what year did world war i begin?", ["1914"], ["World War I began in 1914."]),
    _q("in what year did world war i end?", ["1918"], ["World War I ended in 1918."]),
    _q("in what year did the berlin wall fall?", ["1989"], ["The Berlin Wall fell in 1989."]),
    _q("in what year did the titanic sink?", ["1912"], ["The Titanic sank in 1912."]),
    _q("in what year did columbus first reach the americas?", ["1492"], ["Christopher Columbus first reached the Americas in 1492."]),
    _q("in what year did the french revolution begin?", ["1789"], ["The French Revolution began in 1789."]),
    _q("in what year did the united states declare independence?", ["1776"], ["The United States declared independence in 1776."]),
    # everyday knowledge
    _q("how many days are there in a leap year?", ["366"], ["A leap year has 366 days."]),
    _q("how many minutes are there in an hour?", ["60", "sixty"], ["There are 60 minutes in an hour."]),
    _q("how many hours are there in a day?", ["24", "twenty-four", "twenty four"], ["There are 24 hours in a day."]),
    _q("how many sides does a hexagon have?", ["six", " 6 ", " 6.", " 6,"], ["A hexagon has six sides."]),
    _q("how many continents are there?", ["seven", " 7 ", " 7.", " 7,"], ["There are seven continents."]),
    _q("which musical instrument has 88 keys?", ["piano"], ["A standard piano has 88 keys."]),
    _q("how many strings does a standard guitar have?", ["six", " 6 ", " 6.", " 6,"], ["A standard guitar has six strings."]),
    _q("what is the main ingredient of guacamole?", ["avocado"], ["Avocado is the main ingredient of guacamole."]),
]] + [
    # threads: the follow-ups depend on the pronoun
    [
        _q("who painted the mona lisa?", ["Leonardo", "da Vinci", "Vinci"], ["Leonardo da Vinci painted the Mona Lisa.", "The Mona Lisa hangs in the Louvre in Paris."]),
        _q("in which country was he born?", ["Italy"], ["Leonardo da Vinci was born in Italy.", "Leonardo da Vinci was born in the town of Vinci in 1452."]),
        _q("name another famous painting he made.", ["Last Supper", "Vitruvian", "Ermine", "Salvator Mundi", "Annunciation", "Adoration of the Magi", "Ginevra", "Belle Ferronni", "Virgin of the Rocks", "Saint John", "Madonna"],
           ["The Last Supper is a painting by Leonardo da Vinci.", "The Vitruvian Man is a drawing by Leonardo da Vinci.", "Lady with an Ermine is a painting by Leonardo da Vinci."]),
    ],
    [
        _q("what is the tallest mountain on earth?", ["Everest"], ["Mount Everest is the tallest mountain on Earth above sea level."]),
        _q("on which continent is it?", ["Asia"], ["Mount Everest is in Asia.", "Mount Everest is in the Himalayas."]),
        _q("which two countries does it lie between?", ["Nepal"], ["Mount Everest lies on the border between Nepal and China.", "The Chinese side of Mount Everest is in Tibet."]),
    ],
    [
        _q("who was the first person to walk on the moon?", ["Armstrong"], ["Neil Armstrong was the first person to walk on the Moon."]),
        _q("which mission was he part of?", ["Apollo 11"], ["Neil Armstrong walked on the Moon during the Apollo 11 mission.", "Buzz Aldrin also walked on the Moon during Apollo 11."]),
        _q("in what year did that happen?", ["1969"], ["The Apollo 11 Moon landing took place in 1969.", "Apollo 11 landed on the Moon on July 20, 1969."]),
    ],
    [
        _q("who wrote pride and prejudice?", ["Austen"], ["Jane Austen wrote Pride and Prejudice.", "Pride and Prejudice was published in 1813."]),
        _q("in which country was she born?", ["England", "English", "Britain", "United Kingdom"], ["Jane Austen was born in England.", "Jane Austen was born in 1775 in Steventon, Hampshire."]),
        _q("name another novel she wrote.", ["Emma", "Sense and Sensibility", "Persuasion", "Mansfield Park", "Northanger Abbey"], ["Emma is a novel by Jane Austen.", "Sense and Sensibility is a novel by Jane Austen.", "Persuasion is a novel by Jane Austen."]),
    ],
    [
        _q("what is the largest planet in the solar system?", ["Jupiter"], ["Jupiter is the largest planet in the solar system."]),
        _q("what is it mostly made of?", ["hydrogen"], ["Jupiter is mostly made of hydrogen and helium.", "Jupiter is a gas giant."]),
        _q("which planet is the second largest?", ["Saturn"], ["Saturn is the second-largest planet in the solar system.", "Saturn is known for its rings."]),
    ],
]
