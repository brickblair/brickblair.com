"""Apply the copyedits to the archived essay text and log every change.

Each edit is (old, new, why). Every `old` must appear exactly once.
"""
import pathlib, re, sys

HERE = pathlib.Path(__file__).parent / "essays"

EDITS = {
    "what-are-we-doing-here": [
        ("in fact confirm it", "in fact confirms it", "subject-verb agreement"),
        ("The artist, fan and the ecosystem", "The artist, the fan, and the ecosystem", "parallel list"),
        ("It is a collective fantasy provides magic", "It is a collective fantasy that provides magic", "missing word"),
        ("least commercially-focused artist", "least commercially focused artist", "no hyphen after -ly"),
        ("And, in doing this try to get more", "And, in doing this, try to get more", "comma"),
        ("In other words,  to love", "In other words, to love", "double space"),
    ],
    "we-are-time-prisoners": [
        ("Time is presented as a fact; as the math by which we live, but",
         "Time is presented as a fact, as the math by which we live, but", "semicolon to comma"),
        ("22 minutes of vaudeville", "Twenty-two minutes of vaudeville", "number at start of sentence"),
        ("through a ever narrowing funnel of attention grabbers\n",
         "through an ever-narrowing funnel of attention grabbers.\n\n", "article, hyphen, missing period"),
    ],
    "on-the-zooms-essay": [
        ("a cotton tipped stick", "a cotton-tipped stick", "hyphen"),
        ("open second floor window", "open second-floor window", "hyphen"),
        ("Other people depended me on me.", "Other people depended on me.", "typo"),
        ("Is that because  it", "Is that because it", "double space"),
        ("alternate timeline?  Is it", "alternate timeline? Is it", "double space"),
        ("I  encouraged", "I encouraged", "double space"),
        ("neither amorphous or elliptical", "neither amorphous nor elliptical", "neither/nor"),
    ],
    "two-dollar-coat-qa": [
        ("# What genre is the song?\n\nSinger Songwriter, Acoustic, Folk, Americana, Indie Folk\n",
         "## What genre is the song?\n\nSinger-songwriter, acoustic, folk, Americana, indie folk.\n", "heading level, capitalization"),
        ("## Describe the Track", "## Describe the track", "heading case"),
        ("a new stripped down, vulnerable song", "a new stripped-down, vulnerable song", "hyphen"),
        ("classic acoustic singer songwriters", "classic acoustic singer-songwriters", "hyphen"),
        ("_Nebraska_ , and songs like Townes Van Zandt’s, _Waiting Around to Die._",
         "_Nebraska_, and songs like Townes Van Zandt’s _Waiting Around to Die_.", "punctuation"),
                ("Shortly after I met someone who I would later fall in love with, she sent me a video after she'd been out drinking all night with her friends sitting on cinderblock wall in front of a Brooklyn brownstone, singing the song at the top of her lungs except she was singing it as $3 coat and inflation wasn't even that bad then.",
         "Shortly after I met someone I would later fall in love with, she sent me a video. She'd been out drinking all night with her friends, sitting on a cinderblock wall in front of a Brooklyn brownstone, singing the song at the top of her lungs. Except she was singing it as “Three Dollar Coat,” and inflation wasn't even that bad then.",
         "run-on, missing article"),
        ("No, fortunately. I've been close. I could see it happening, for a couple of reasons. One is that although whether through my body as a carpenter or laborer or through my mind as a writer I've always been able to make a living. But I’m also really fucking bad at managing that money so I've been in very dire straits before but the ability to earn some money has often saved me.",
         "No, fortunately. But I've been close. I could see it happening, for a couple of reasons. One is that, whether through my body as a carpenter or laborer or through my mind as a writer, I've always been able to make a living. But I’m also really fucking bad at managing that money, so I've been in very dire straits before. The ability to earn some money has often saved me.",
         "garbled sentence, run-on"),
        ("leading me to a place that would include losing everything materially and probably losing and alienating the people who would otherwise be there for me luckily, I got that under control, since my late 30s.",
         "leading me to a place where I'd lose everything materially, and probably lose and alienate the people who would otherwise be there for me. Luckily, I've had that under control since my late 30s.",
         "run-on, tense"),
                ("but then it was just smelly dead person's clothes", "but back then it was just smelly dead people's clothes", "clarity"),
        ("three quarter length overcoat", "three-quarter-length overcoat", "hyphens"),
        ("Army surplus stuff", "army-surplus stuff", "hyphen"),
        ("because it was opposite of the $2500", "because it was the opposite of the $2,500", "missing article, number"),
        ("produced by Brick Blair and Robert Farren", "produced by Brick Blair and Robert Farren", "(unchanged)"),
        ("Two Dollar Coat was recorded by and produced by", "Two Dollar Coat was recorded and produced by", "wording"),
        ("when Rob moved his studio in a large industrial Brooklyn loft.", "when Rob moved his studio into a large industrial Brooklyn loft.", "preposition"),
        ("large sound absorbing and reflecting panels", "large sound-absorbing and reflecting panels", "hyphen"),
        ("emotion of the song.\n\n“When we started working together, I felt self conscious recording intricate parts under pressure in the studio. I use a lot",
         "emotion of the song.\n\n“When we started working together, I felt self-conscious recording intricate parts under pressure in the studio,” said Brick. “I use a lot",
         "attribution, hyphen"),
        ("But, in my studio, with unlimited time", "But in my studio, with unlimited time", "comma"),
        ("I already had a decent studio but I got rid of some crap", "I already had a decent studio, but I got rid of some crap", "comma"),
        ("use the studio as a songwriting and production tool.\n", "use the studio as a songwriting and production tool.”\n", "closing quote"),
                ("The album is called Unreleased and is focused on songs", "The album is called _Unreleased_ and is focused on songs", "italic title"),
        ("The EP is called Widow & Orphan control is more stripped down.\n\nTwo Dollar Coat is from the EP and I was released as a single.",
         "The EP, called _Widow & Orphan Control_, is more stripped down.\n\nTwo Dollar Coat is from the EP and was released as a single.",
         "garbled sentence, title"),
        ("\"Almost all my gear is from charity shops and estate sales,” said Brick. \"I rebuild it then write and record with it.",
         "“Almost all my gear is from charity shops and estate sales,” said Brick. “I rebuild it, then write and record with it.", "curly quotes, comma"),
        ("an early 70s Japanese Epiphone dreadnought", "an early-’70s Japanese Epiphone dreadnought", "decade"),
        ("The cover image is a video still of a video I shot", "The cover image is a still from a video I shot", "wording"),
        ("so I just sung the rest of the song acapella from memory", "so I just sang the rest of the song a cappella from memory", "verb form, spelling"),
        ("Acoustic guitar and vocals - Brick Blair", "Acoustic guitar and vocals: Brick Blair", "punctuation"),
        ("Lyrics and music - Brick Blair", "Lyrics and music: Brick Blair", "punctuation"),
        ("Produced by Brick Blair and Robert Farren\n", "Produced by Brick Blair and Robert Farren\n", "(unchanged)"),
        ("Engineered by Robert Farren", "Engineered by Robert Farren", "(unchanged)"),
        ("Mastered by Michele Mancini at Demifuge Mastering in Los Angeles, CA.", "Mastered by Michele Mancini at Demifuge Mastering, Los Angeles", "punctuation"),
    ],
}

log = []
for slug, edits in EDITS.items():
    p = HERE / f"{slug}.orig.md"
    text = p.read_text().replace("\xa0", " ")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    if slug == "two-dollar-coat-qa":
        text, k = re.subn(r"(?m)^(?:\*\*Brick\*\*\.|Brick\.)\s+", "**Brick:** ", text)
        log.append((slug, "consistent speaker label", f"Brick. ({k} answers)", "**Brick:**"))
    for old, new, why in edits:
        n = text.count(old)
        if n != 1:
            sys.exit(f"{slug}: expected 1 match, found {n}: {old[:70]!r}")
        if old != new:
            text = text.replace(old, new)
            log.append((slug, why, old.strip()[:90], new.strip()[:90]))
    text = re.sub(r"[ \t]+\n", "\n", text)  # trailing spaces left by the export
    (HERE / f"{slug}.md").write_text(text)

for slug, why, old, new in log:
    print(f"{slug} | {why} | {old} -> {new}")
print(len(log), "edits")
