"""
DARK STUDIO AAA v2.0 — DARK MULTILINGUAL FACTORY
==================================================
Orquestrador completo para produção multilingual de YouTube Shorts.

Coordena: DarkEdgeTTS v2 + DarkMultilingualAgent v2 + vidIQ MCP pipeline
Suporte: PT-BR, EN, ES, DE, FR, IT, AR, JA, ZH, KO, PL

Arquitetura:
  DarkMultilingualFactory
  ├── CINEMATIC DIRECTOR   → determina estilo visual e prompt de vídeo
  ├── AUDIO MASTER         → gera narração via DarkEdgeTTS v2
  ├── IMAGE ENGINE         → gera thumbnail via vidIQ
  ├── VIDEO GENERATOR      → gera vídeo via vidIQ
  ├── VIDEO EDITOR PRO     → compõe áudio + vídeo via vidIQ
  ├── CREATIVE QA          → valida duração, hook, qualidade
  ├── ASSET MANAGER        → faz upload para YouTube via vidIQ
  └── MULTILINGUAL AGENT   → gera traduções de metadados para outros idiomas

Uso:
  factory = DarkMultilingualFactory()
  result = factory.produce(canal="Esquina do Medo", idioma="en", nicho="horror")
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# ─────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO: CANAIS × IDIOMAS
# ─────────────────────────────────────────────────────────────────

FACTORY_CONFIG: Dict[str, Dict] = {
    "Esquina do Medo": {
        "id": "UCwuyz5ABF6ooQUn2HwG9xHQ",
        "nicho": "horror",
        "idioma_base": "pt",
        "idiomas_alvo": ["en", "es", "de", "fr"],
        "serie_pt": "Esquina do Medo",
        "series": {
            "en": "Fear Corner",
            "es": "Esquina del Miedo",
            "de": "Angstecke",
            "fr": "Le Coin de la Peur",
            "it": "L'Angolo della Paura",
        },
        "cta": {
            "pt": "Siga a Esquina do Medo para mais histórias aterrorizantes.",
            "en": "Follow Fear Corner for more terrifying stories every day.",
            "es": "Síguenos para más historias aterradoras cada día.",
            "de": "Folge Angstecke für mehr erschreckende Geschichten jeden Tag.",
            "fr": "Suivez Le Coin de la Peur pour plus d'histoires terrifiantes.",
        },
    },
    "Mente de Aço": {
        "id": "UCPRWgHoI85u-gmZmS9uVbqA",
        "nicho": "motivacional",
        "idioma_base": "pt",
        "idiomas_alvo": ["en", "es", "de", "fr", "it", "ar"],
        "serie_pt": "Mente de Aço",
        "series": {
            "en": "Iron Mind",
            "es": "Mente de Acero",
            "de": "Eiserner Geist",
            "fr": "L'Esprit d'Acier",
            "it": "Mente d'Acciaio",
            "ar": "العقل الحديدي",
        },
        "cta": {
            "pt": "Siga a Mente de Aço para desenvolver uma mente invencível.",
            "en": "Subscribe and turn on notifications — Iron Mind drops every Monday.",
            "es": "Suscríbete a Mente de Acero — cada semana, contenido que transforma.",
            "de": "Abonniere Eiserner Geist für wöchentliche mentale Stärke.",
            "fr": "Abonnez-vous à L'Esprit d'Acier — chaque semaine.",
        },
    },
    "Intelligentia Nova": {
        "id": "UCoGPdIQM2Bt5zSlV0DW0HQg",
        "nicho": "tecnologia",
        "idioma_base": "pt",
        "idiomas_alvo": ["en", "es", "de", "fr", "it", "zh"],
        "serie_pt": "Intelligentia Nova",
        "series": {
            "en": "Nova Intelligence",
            "es": "Intelligentia Nova",
            "de": "Dark Tech",
            "fr": "Intelligence Nova",
            "zh": "智能新纪元",
        },
        "cta": {
            "pt": "Siga a Intelligentia Nova para ficar à frente do futuro.",
            "en": "Follow Nova Intelligence — technology that changes the world.",
            "es": "Sigue Intelligentia Nova — tecnología del futuro.",
            "de": "Folge Dark Tech — Technologie, die die Welt verändert.",
        },
    },
    "AquaZen Relax": {
        "id": "UC89YZqbZ02RTaT2FYepPHCQ",
        "nicho": "relaxamento",
        "idioma_base": "pt",
        "idiomas_alvo": ["en", "es", "fr", "de", "ja", "ko"],
        "serie_pt": "AquaZen",
        "series": {
            "en": "AquaZen",
            "es": "AquaZen",
            "fr": "AquaZen",
            "de": "AquaZen",
            "ja": "アクアゼン",
            "ko": "아쿠아젠",
        },
        "cta": {
            "pt": "Respira. Relaxa. Siga o AquaZen para mais momentos de paz.",
            "en": "Breathe. Relax. Follow AquaZen for more peaceful moments.",
            "es": "Respira. Relájate. Sigue AquaZen para más paz.",
            "de": "Atme. Entspanne. Folge AquaZen für mehr Frieden.",
            "ja": "息をして。リラックス。もっと平和なひとときを。",
        },
    },
    "Bastidores do Tempo": {
        "id": "UCMinaADQVJ6QbbhOr_idVdA",
        "nicho": "historia",
        "idioma_base": "pt",
        "idiomas_alvo": ["en", "es", "de", "fr", "it", "ar", "pl"],
        "serie_pt": "Bastidores do Tempo",
        "series": {
            "en": "Behind Time",
            "es": "Tras el Tiempo",
            "de": "Hinter der Zeit",
            "fr": "Dans les Coulisses du Temps",
            "pl": "Za Kulisami Czasu",
        },
        "cta": {
            "pt": "Siga os Bastidores do Tempo — a história que não contaram para você.",
            "en": "Follow Behind Time — the history they never told you.",
            "es": "Sigue Tras el Tiempo — la historia que no te contaron.",
            "de": "Folge Hinter der Zeit — die Geschichte, die man dir nie erzählte.",
        },
    },
    "Projeto Secreto": {
        "id": "UCOfXd8Hf_83Y2VHWmj3f3Vg",
        "nicho": "misterio",
        "idioma_base": "pt",
        "idiomas_alvo": ["en", "es", "de", "fr", "it"],
        "serie_pt": "Projeto Secreto",
        "series": {
            "en": "Secret Project",
            "es": "Proyecto Secreto",
            "de": "Geheimes Projekt",
            "fr": "Projet Secret",
            "it": "Progetto Segreto",
        },
        "cta": {
            "pt": "Siga o Projeto Secreto — os segredos que eles tentam esconder.",
            "en": "Follow Secret Project — the secrets they try to hide.",
            "es": "Sigue Proyecto Secreto — los secretos que intentan ocultar.",
            "de": "Folge Geheimes Projekt — die Geheimnisse, die sie verbergen wollen.",
        },
    },
}

# ─────────────────────────────────────────────────────────────────
# SCRIPTS PRÉ-ESCRITOS POR NICHO × IDIOMA
# ─────────────────────────────────────────────────────────────────

SCRIPTS: Dict[str, Dict[str, List[str]]] = {
    "horror": {
        "en": [
            "Have you ever heard of the town that disappeared overnight? In 1872, the entire population of a small coastal village in New England simply vanished. No bodies. No signs of struggle. Just empty houses and a strange symbol burned into the church door. To this day, nobody knows what happened. And the local government REFUSES to talk about it. Follow Fear Corner for more terrifying stories every day.",
            "In 1947, a U.S. Navy ship sent out a distress signal from the middle of the Pacific Ocean. When rescuers arrived, they found the vessel completely intact — engines running, food still warm on the table. But every single crew member had vanished without a trace. The case was classified for 40 years. We found the documents. Follow Fear Corner for more secrets they tried to bury.",
            "There's a bridge in Japan where the police stopped counting. Since the 1950s, thousands of people have reported hearing voices beneath it — voices calling their name. Scientists have studied it. Psychologists have analyzed it. Nobody can explain it. What is under that bridge? Follow Fear Corner — new horror every day.",
        ],
        "es": [
            "¿Alguna vez has escuchado sobre el pueblo que desapareció de la noche a la mañana? En 1872, toda la población de una pequeña aldea costera simplemente se esfumó. Sin cuerpos. Sin señales de lucha. Solo casas vacías y un extraño símbolo quemado en la puerta de la iglesia. Hasta hoy, nadie sabe qué pasó. Y el gobierno local SE NIEGA a hablar de ello. Síguenos para más historias aterradoras cada día.",
            "En 1947, un barco de la Marina de los EE.UU. envió una señal de auxilio desde el Pacífico. Cuando llegaron los rescatistas, encontraron el barco intacto — motores en marcha, comida aún caliente. Pero toda la tripulación había desaparecido sin dejar rastro. El caso fue clasificado durante 40 años. Encontramos los documentos. Síguenos para más secretos.",
        ],
        "de": [
            "Hast du jemals von der Stadt gehört, die über Nacht verschwand? Im Jahr 1872 verschwand die gesamte Bevölkerung eines kleinen Küstendorfes in Neuengland spurlos. Keine Leichen. Keine Anzeichen von Kampf. Nur leere Häuser und ein seltsames Symbol, das in die Kirchentür gebrannt worden war. Bis heute weiß niemand, was passiert ist. Und die Lokalbehörden WEIGERN sich zu sprechen. Folge Angstecke für mehr erschreckende Geschichten jeden Tag.",
            "1947 sandte ein US-Marine-Schiff ein Notsignal aus dem Pazifik. Als die Retter ankamen, fanden sie das Schiff vollständig intakt — Motoren liefen, Essen noch warm auf dem Tisch. Aber jedes einzelne Besatzungsmitglied war spurlos verschwunden. Der Fall wurde 40 Jahre lang als Geheimsache eingestuft. Wir haben die Dokumente gefunden. Folge uns für mehr verborgene Geheimnisse.",
        ],
        "fr": [
            "Avez-vous entendu parler du village qui a disparu du jour au lendemain? En 1872, toute la population d'un petit village côtier de Nouvelle-Angleterre s'est simplement évaporée. Aucun corps. Aucun signe de lutte. Juste des maisons vides et un étrange symbole brûlé dans la porte de l'église. Jusqu'à aujourd'hui, personne ne sait ce qui s'est passé. Et les autorités locales REFUSENT d'en parler. Suivez Le Coin de la Peur pour plus d'histoires terrifiantes.",
        ],
        "it": [
            "Avete mai sentito del villaggio che scomparve durante la notte? Nel 1872, l'intera popolazione di un piccolo villaggio costiero del New England svanì nel nulla. Nessun corpo. Nessun segno di lotta. Solo case vuote e uno strano simbolo bruciato sulla porta della chiesa. Ancora oggi, nessuno sa cosa è successo. E le autorità locali SI RIFIUTANO di parlarne. Segui L'Angolo della Paura per altre storie terrificanti ogni giorno.",
        ],
    },
    "motivacional": {
        "en": [
            "Your brain physically rewires itself when you repeat a habit for 21 days. That's not motivation — that's neuroscience. Every time you push through discomfort, you're literally building new neural pathways. The people who dominate their field aren't more talented. They're more consistent. What you do in the next 21 days determines who you become. Start now. Subscribe and turn on notifications — Iron Mind drops every Monday.",
            "The difference between the person you are today and the person you want to become is not talent. It's not luck. It's not even time. It's what you do when no one is watching. When you're tired. When you want to quit. That's the moment that defines everything. Iron Mind — training the mind is the hardest and most important thing you'll ever do. Subscribe.",
            "Studies show that 92% of people who set goals never achieve them. Not because they lack ability. Because they lack a system. A system that runs even when motivation fails. That's what Iron Mind is about — building the architecture of success in your brain. Subscribe and turn on notifications.",
        ],
        "es": [
            "Tu cerebro se recablea físicamente cuando repites un hábito durante 21 días. Eso no es motivación — es neurociencia. Cada vez que superas el malestar, literalmente estás construyendo nuevas vías neuronales. Las personas que dominan su campo no son más talentosas. Son más constantes. Lo que hagas en los próximos 21 días determina en quién te conviertes. Comienza ahora. Suscríbete — Mente de Acero cada semana.",
        ],
        "de": [
            "Dein Gehirn verdrahtet sich physisch neu, wenn du eine Gewohnheit 21 Tage lang wiederholst. Das ist keine Motivation — das ist Neurowissenschaft. Jedes Mal, wenn du Unbehagen überwindest, baust du buchstäblich neue neuronale Pfade. Die Menschen, die in ihrem Bereich dominieren, sind nicht talentierter. Sie sind konsequenter. Was du in den nächsten 21 Tagen tust, bestimmt, wer du wirst. Fang jetzt an. Abonniere Eiserner Geist.",
        ],
        "fr": [
            "Votre cerveau se recâble physiquement lorsque vous répétez une habitude pendant 21 jours. Ce n'est pas de la motivation — c'est de la neuroscience. Chaque fois que vous surmontez un inconfort, vous construisez littéralement de nouvelles voies neuronales. Les gens qui dominent leur domaine ne sont pas plus talentueux. Ils sont plus constants. Ce que vous faites dans les 21 prochains jours détermine qui vous devenez. Abonnez-vous à L'Esprit d'Acier.",
        ],
        "ar": [
            "يُعيد دماغك توصيل نفسه جسديًا عندما تكرر عادةً لمدة 21 يومًا. هذا ليس تحفيزًا — هذا علم الأعصاب. في كل مرة تتغلب فيها على الانزعاج، تبني حرفيًا مسارات عصبية جديدة. الناس الذين يهيمنون على مجالهم ليسوا أكثر موهبة. إنهم أكثر ثباتًا. ما تفعله في الـ 21 يومًا القادمة يحدد من ستصبح. ابدأ الآن. اشترك في العقل الحديدي.",
        ],
    },
    "tecnologia": {
        "en": [
            "Scientists have created an AI that predicts financial crises with 94% accuracy — and no bank wants you to know about it. It analyzed 150 years of market data and found patterns invisible to human analysts. The last time it issued a warning was 48 hours before the 2008 collapse. It's currently running. And it's not saying good things. Follow Nova Intelligence for the technology they don't want you to understand.",
            "A chip that replaces human neurons just entered clinical trials. It doesn't treat diseases — it upgrades the brain. Memory. Processing speed. Focus. The first human subjects reported seeing in colors that don't exist in nature. This isn't science fiction. This is what's happening right now. Follow Nova Intelligence to stay ahead of the future.",
        ],
        "de": [
            "Wissenschaftler haben eine KI entwickelt, die Finanzkrisen mit 94% Genauigkeit vorhersagt — und keine Bank will, dass du das weißt. Sie analysierte 150 Jahre Marktdaten und fand Muster, die für menschliche Analysten unsichtbar sind. Das letzte Mal gab sie 48 Stunden vor dem Zusammenbruch 2008 eine Warnung aus. Sie läuft gerade. Und sie sagt nichts Gutes. Folge Dark Tech für Technologie, die sie nicht wollen, dass du verstehst.",
            "Ein Chip, der menschliche Neuronen ersetzt, befindet sich gerade in klinischen Tests. Er behandelt keine Krankheiten — er aktualisiert das Gehirn. Gedächtnis. Verarbeitungsgeschwindigkeit. Fokus. Die ersten menschlichen Versuchspersonen berichteten, Farben zu sehen, die in der Natur nicht existieren. Das ist keine Science-Fiction. Das passiert gerade jetzt. Folge Dark Tech.",
        ],
        "fr": [
            "Des scientifiques ont créé une IA qui prédit les crises financières avec 94% de précision — et aucune banque ne veut que vous le sachiez. Elle a analysé 150 ans de données de marché et trouvé des modèles invisibles aux analystes humains. La dernière fois qu'elle a émis un avertissement, c'était 48 heures avant l'effondrement de 2008. Elle tourne en ce moment. Et elle ne dit pas de bonnes choses. Suivez Intelligence Nova.",
        ],
    },
    "relaxamento": {
        "en": [
            "Take a deep breath. Right now. Feel the tension leave your shoulders. You are exactly where you need to be. This moment, this breath, this peace — it's yours. Nature heals what busyness breaks. Let the sound of water carry everything away. Subscribe to AquaZen for more peaceful moments.",
            "Research shows that 10 minutes listening to natural water sounds reduces cortisol by 27%. Not a supplement. Not a drug. Just water and presence. Close your eyes. Let go. Subscribe to AquaZen — nature's healing, every day.",
        ],
        "de": [
            "Atme tief ein. Jetzt. Spüre, wie die Anspannung deine Schultern verlässt. Du bist genau dort, wo du sein musst. Dieser Moment, dieser Atemzug, dieser Frieden — er gehört dir. Die Natur heilt, was die Hektik zerbrochen hat. Lass das Geräusch des Wassers alles davontragen. Abonniere AquaZen für mehr friedliche Momente.",
        ],
        "fr": [
            "Respirez profondément. Maintenant. Sentez la tension quitter vos épaules. Vous êtes exactement là où vous devez être. Ce moment, ce souffle, cette paix — c'est le vôtre. La nature guérit ce que l'agitation brise. Laissez le son de l'eau emporter tout. Abonnez-vous à AquaZen pour plus de moments paisibles.",
        ],
        "ja": [
            "深呼吸をしてください。今すぐ。肩の力が抜けていくのを感じてください。あなたは今、いるべき場所にいます。この瞬間、この息吹、この平和 — それはあなたのものです。自然は、忙しさが壊したものを癒します。水の音がすべてを運び去るのを感じてください。アクアゼンを登録して、もっと平和なひとときを。",
        ],
    },
    "historia": {
        "en": [
            "In 1943, the U.S. government conducted an experiment so disturbing that official records were sealed for 50 years. They wanted to know if a warship could be made invisible to radar. What happened to the USS Eldridge that night changed the lives of its crew forever. Some say it was teleported. Others say the men went mad. The government says it never happened. We found the evidence. Follow Behind Time.",
            "There's a city under the ocean off the coast of Japan. It's not a myth. It's not a legend. Divers found it in 1986, and nobody can explain how it got there. The structures are too precise to be natural. The government classified the findings. The original diving team was silenced. This is what they don't want you to know. Follow Behind Time for history they tried to bury.",
        ],
        "de": [
            "Im Jahr 1943 führte die US-Regierung ein Experiment durch, das so verstörend war, dass offizielle Akten 50 Jahre lang versiegelt wurden. Sie wollten wissen, ob ein Kriegsschiff für Radar unsichtbar gemacht werden könnte. Was in jener Nacht mit der USS Eldridge geschah, veränderte das Leben ihrer Besatzung für immer. Einige sagen, sie wurde teleportiert. Andere sagen, die Männer wurden wahnsinnig. Die Regierung sagt, es ist nie passiert. Wir haben die Beweise gefunden. Folge Hinter der Zeit.",
        ],
        "es": [
            "En 1943, el gobierno de EE.UU. llevó a cabo un experimento tan perturbador que los registros oficiales estuvieron sellados durante 50 años. Querían saber si un buque de guerra podía hacerse invisible al radar. Lo que le sucedió al USS Eldridge esa noche cambió para siempre la vida de su tripulación. Algunos dicen que fue teletransportado. Otros dicen que los hombres enloquecieron. El gobierno dice que nunca sucedió. Encontramos la evidencia. Sigue Tras el Tiempo.",
        ],
        "fr": [
            "En 1943, le gouvernement américain a mené une expérience si troublante que les dossiers officiels ont été scellés pendant 50 ans. Ils voulaient savoir si un navire de guerre pouvait être rendu invisible au radar. Ce qui est arrivé à l'USS Eldridge cette nuit-là a changé la vie de son équipage pour toujours. Certains disent qu'il a été téléporté. D'autres disent que les hommes sont devenus fous. Le gouvernement dit que cela n'a jamais eu lieu. Suivez Dans les Coulisses du Temps.",
        ],
    },
    "misterio": {
        "en": [
            "In 1962, a classified government file was leaked. It described a project so secret that only 7 people in the world had access to it. The file listed coordinates, dates, and something called Operation Blacklight. What happened at those coordinates on those dates was never made public. Until now. Follow Secret Project — the secrets they tried to bury.",
        ],
        "es": [
            "En 1962, se filtró un archivo gubernamental clasificado. Describía un proyecto tan secreto que solo 7 personas en el mundo tenían acceso a él. El archivo enumeraba coordenadas, fechas y algo llamado Operación Luz Negra. Lo que ocurrió en esas coordenadas en esas fechas nunca fue divulgado públicamente. Hasta ahora. Sigue Proyecto Secreto.",
        ],
        "de": [
            "Im Jahr 1962 wurde eine geheime Regierungsakte durchgesickert. Sie beschrieb ein Projekt, das so geheim war, dass nur 7 Menschen auf der Welt Zugang dazu hatten. Die Akte listete Koordinaten, Daten und etwas namens Operation Schwarzlicht auf. Was an jenen Koordinaten an jenen Daten geschah, wurde nie öffentlich gemacht. Bis jetzt. Folge Geheimes Projekt.",
        ],
    },
}

# ─────────────────────────────────────────────────────────────────
# ESTILOS VISUAIS POR NICHO
# ─────────────────────────────────────────────────────────────────

ESTILOS_VISUAIS: Dict[str, Dict] = {
    "horror": {
        "thumbnail_style": "dark atmospheric, horror cinematographic, deep shadows, cold blue-green light, disturbing mystery element",
        "video_prompt": "cinematic horror scene, abandoned location, dark atmospheric lighting, film grain, cold blue light, deep shadows, mystery element, 9:16 vertical format",
        "color_palette": "dark blues, blacks, cold greens",
        "typography": "distressed, horror font",
    },
    "motivacional": {
        "thumbnail_style": "dramatic portrait photography, high contrast, desaturated, intense human expression, powerful typography",
        "video_prompt": "dramatic motivational scene, person in intense focus, dark atmosphere with determination, cinematic lighting, 9:16 vertical format",
        "color_palette": "high contrast black and white, deep reds",
        "typography": "bold, impactful",
    },
    "tecnologia": {
        "thumbnail_style": "futuristic tech aesthetic, neon blue/cyan accents, dark background, data visualization elements",
        "video_prompt": "futuristic technology scene, data flowing, neural networks visualized, clean minimal aesthetic, blue/cyan tones, 9:16 vertical format",
        "color_palette": "dark navy, neon blue, cyan, white",
        "typography": "modern, tech-forward, clean",
    },
    "relaxamento": {
        "thumbnail_style": "serene nature photography, soft blue-green tones, gentle water element, peaceful",
        "video_prompt": "peaceful nature scene, gentle water movement, soft natural lighting, serene atmosphere, 4K quality, 9:16 vertical format",
        "color_palette": "soft blues, greens, warm golds",
        "typography": "light, elegant, minimal",
    },
    "historia": {
        "thumbnail_style": "documentary cinematic, warm sepia/amber tones, archival aesthetic, historical element prominent",
        "video_prompt": "cinematic historical scene, archival footage aesthetic, dramatic warm lighting, period-accurate settings, documentary style, 9:16 vertical format",
        "color_palette": "warm sepia, amber, dark browns",
        "typography": "classic serif, archival",
    },
    "misterio": {
        "thumbnail_style": "mysterious conspiracy aesthetic, classified document look, dark atmosphere, magnifying glass or hidden symbol element",
        "video_prompt": "mysterious investigative scene, classified document aesthetic, dark atmosphere, conspiracy thriller style, 9:16 vertical format",
        "color_palette": "dark greens, yellows, blacks",
        "typography": "typewriter, classified",
    },
}

# ─────────────────────────────────────────────────────────────────
# HASHTAGS POR IDIOMA × NICHO
# ─────────────────────────────────────────────────────────────────

HASHTAGS: Dict[str, Dict[str, str]] = {
    "horror": {
        "pt": "#EsquinaDoMedo #Horror #Misterio #HistoriasDeHorror #TerrorBrasileiro",
        "en": "#FearCorner #Horror #Mystery #TrueHorror #ScaryStories #Paranormal",
        "es": "#EsquinaDelMiedo #Horror #Misterio #HistoriasDeMiedo #Terror",
        "de": "#Angstecke #Horror #Grusel #Mysterium #HorrorDeutsch",
        "fr": "#CoinDeLaPeur #Horreur #Mystère #PeurFrançaise #Effrayant",
        "it": "#AngoloDellaParaura #Horror #Mistero #PauraNotte",
    },
    "motivacional": {
        "pt": "#MenteDeAco #MenteForte #Disciplina #ForcaMental #Motivacao",
        "en": "#IronMind #MentalStrength #Psychology #Discipline #Mindset",
        "es": "#MenteDeAcero #FuerzaMental #Disciplina #Psicologia #Motivacion",
        "de": "#EisernerGeist #MentaleStärke #Disziplin #Psychologie #Motivation",
        "fr": "#EspritDAcier #ForceMetale #Discipline #Psychologie #Motivation",
        "ar": "#العقل_الحديدي #قوة_عقلية #الانضباط #علم_النفس #التحفيز",
    },
    "tecnologia": {
        "pt": "#IntelligenteNova #InteligenciaArtificial #Tecnologia #Ciencia #Futuro",
        "en": "#NovaIntelligence #ArtificialIntelligence #Technology #Science #Future",
        "de": "#DarkTech #KünstlicheIntelligenz #Technologie #Wissenschaft #Zukunft",
        "fr": "#IntelligenceNova #IntelligenceArtificielle #Technologie #Science #Futur",
        "zh": "#暗黑科技 #人工智能 #科技 #科学 #未来",
    },
    "relaxamento": {
        "pt": "#AquaZen #Relaxamento #SonsDaNatureza #Meditacao #Paz",
        "en": "#AquaZen #Relaxation #NatureSounds #Meditation #Peace",
        "de": "#AquaZen #Entspannung #Naturgeräusche #Meditation #Frieden",
        "fr": "#AquaZen #Relaxation #SonsNature #Méditation #Paix",
        "ja": "#アクアゼン #リラクゼーション #自然の音 #瞑想 #平和",
    },
    "historia": {
        "pt": "#BastidoresDoTempo #HistoriaSecreta #Misterio #Segredos #Conspiração",
        "en": "#BehindTime #SecretHistory #Mystery #HiddenTruth #Conspiracy",
        "de": "#HinterDerZeit #GeheimeGeschichte #Mysterium #VerborgeneWahrheit",
        "es": "#TrasElTiempo #HistoriaSecreta #Misterio #Conspiracion",
        "fr": "#CoulissesTemps #HistoireSecrète #Mystère #VéritéCachée",
    },
    "misterio": {
        "pt": "#ProjetoSecreto #Conspiracao #Misterio #Segredos #DarkStudio",
        "en": "#SecretProject #Conspiracy #Mystery #HiddenSecrets #DarkStudio",
        "es": "#ProyectoSecreto #Conspiracion #Misterio #SecretosOcultos",
        "de": "#GeheimesProjekt #Verschwörung #Mysterium #VerborgenGeheimnisse",
    },
}

# ─────────────────────────────────────────────────────────────────
# PRODUCTION RESULT
# ─────────────────────────────────────────────────────────────────

@dataclass
class ProductionResult:
    """Resultado de uma produção multilingual."""
    canal: str
    idioma: str
    nicho: str
    serie_nome: str
    episodio: int
    titulo: str
    descricao: str
    tags: List[str]
    script: str
    voz_edge: str
    thumbnail_style: str
    video_prompt: str
    cta: str
    hashtags: str
    ai_generated: bool = True
    ai_disclosure: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "pendente"
    video_url: Optional[str] = None
    qa_score: Optional[int] = None
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "canal": self.canal,
            "idioma": self.idioma,
            "nicho": self.nicho,
            "serie_nome": self.serie_nome,
            "episodio": self.episodio,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "tags": self.tags,
            "script": self.script,
            "voz_edge": self.voz_edge,
            "thumbnail_style": self.thumbnail_style,
            "video_prompt": self.video_prompt,
            "cta": self.cta,
            "hashtags": self.hashtags,
            "ai_generated": self.ai_generated,
            "ai_disclosure": self.ai_disclosure,
            "timestamp": self.timestamp,
            "status": self.status,
            "video_url": self.video_url,
            "qa_score": self.qa_score,
            "errors": self.errors,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────────────────────────
# DARK MULTILINGUAL FACTORY
# ─────────────────────────────────────────────────────────────────

class DarkMultilingualFactory:
    """
    Orquestrador completo para produção multilingual de YouTube Shorts.

    Arquitetura de agentes:
      CINEMATIC DIRECTOR → AUDIO MASTER → IMAGE ENGINE →
      VIDEO GENERATOR → VIDEO EDITOR PRO → CREATIVE QA →
      ASSET MANAGER → MULTILINGUAL AGENT (metadata translations)
    """

    VERSION = "1.0.0"

    # Mapa de vozes por idioma (Edge Neural)
    VOZES: Dict[str, str] = {
        "pt": "pt-BR-AntonioNeural",
        "en": "en-US-AriaNeural",
        "es": "es-ES-ElviraNeural",
        "de": "de-DE-KatjaNeural",
        "fr": "fr-FR-DeniseNeural",
        "it": "it-IT-ElsaNeural",
        "ar": "ar-SA-ZariyahNeural",
        "ja": "ja-JP-NanamiNeural",
        "ko": "ko-KR-SunHiNeural",
        "zh": "zh-CN-XiaoxiaoNeural",
        "pl": "pl-PL-ZofiaNeural",
    }

    # vidIQ voice IDs confirmados
    VIDIQ_VOICES: Dict[str, str] = {
        "pt": "33B4UnXyTNbgLmdEDh5P",    # Keren — PT-BR female
        "en": "N2lVS1w4EtoT3dr4eOWO",    # Callum — EN male authoritative
    }

    def __init__(self, output_dir: str = "outputs/factory"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._script_index: Dict[str, int] = {}  # rotate scripts

    def _get_script(self, nicho: str, idioma: str, episodio: int) -> str:
        """Retorna script pré-escrito para o nicho e idioma, rotacionando por episódio."""
        scripts_nicho = SCRIPTS.get(nicho, {})
        scripts_idioma = scripts_nicho.get(idioma, [])

        if not scripts_idioma:
            # Fallback: tentar inglês
            scripts_idioma = scripts_nicho.get("en", [])

        if not scripts_idioma:
            return f"[SCRIPT_PENDENTE_{idioma.upper()}_{nicho.upper()}]"

        idx = (episodio - 1) % len(scripts_idioma)
        return scripts_idioma[idx]

    def _build_title(self, canal: str, idioma: str, episodio: int, nicho: str) -> str:
        """Gera título padrão por canal, idioma e episódio."""
        cfg = FACTORY_CONFIG.get(canal, {})
        series = cfg.get("series", {})
        serie_nome = series.get(idioma, cfg.get("serie_pt", canal))

        titulos_base = {
            "horror": {
                "en": "THE TOWN THAT VANISHED OVERNIGHT",
                "es": "EL PUEBLO QUE DESAPARECIÓ DE LA NOCHE A LA MAÑANA",
                "de": "DIE STADT, DIE ÜBER NACHT VERSCHWAND",
                "fr": "LE VILLAGE QUI A DISPARU DU JOUR AU LENDEMAIN",
                "it": "IL VILLAGGIO CHE SCOMPARVE DURANTE LA NOTTE",
            },
            "motivacional": {
                "en": "YOUR BRAIN IS LYING TO YOU",
                "es": "TU CEREBRO TE MIENTE",
                "de": "DEIN GEHIRN LÜGT DICH AN",
                "fr": "TON CERVEAU TE MENT",
                "ar": "دماغك يكذب عليك",
            },
            "tecnologia": {
                "en": "THE AI THAT SEES YOUR FUTURE",
                "de": "DIE KI, DIE DEINE ZUKUNFT SIEHT",
                "fr": "L'IA QUI VOIT VOTRE AVENIR",
                "zh": "预见未来的人工智能",
            },
            "relaxamento": {
                "en": "OCEAN WAVES FOR DEEP RELAXATION 🌊",
                "de": "MEERESWELLEN ZUR TIEFEN ENTSPANNUNG 🌊",
                "fr": "VAGUES DE L'OCÉAN POUR LA RELAXATION 🌊",
                "ja": "深いリラクゼーションのための海の波 🌊",
            },
            "historia": {
                "en": "THE EXPERIMENT THEY TRIED TO ERASE FROM HISTORY",
                "de": "DAS EXPERIMENT, DAS SIE AUS DER GESCHICHTE TILGEN WOLLTEN",
                "es": "EL EXPERIMENTO QUE INTENTARON BORRAR DE LA HISTORIA",
                "fr": "L'EXPÉRIENCE QU'ILS ONT ESSAYÉ D'EFFACER DE L'HISTOIRE",
            },
            "misterio": {
                "en": "THE SECRET FILE THEY NEVER WANTED YOU TO FIND",
                "es": "EL ARCHIVO SECRETO QUE NUNCA QUISIERON QUE ENCONTRARAS",
                "de": "DIE GEHEIMAKTE, DIE SIE NIE FINDEN SOLLTEN",
            },
        }

        titulo_base = titulos_base.get(nicho, {}).get(idioma, f"[TÍTULO EP. {episodio}]")
        return f"{serie_nome} Ep.{episodio} — {titulo_base}"

    def _build_description(self, canal: str, idioma: str, serie_nome: str, cta: str, nicho: str) -> str:
        """Gera descrição padronizada com CTA e hashtags."""
        cfg = FACTORY_CONFIG.get(canal, {})
        hashtags = HASHTAGS.get(nicho, {}).get(idioma, f"#{serie_nome.replace(' ', '')} #DarkStudio")

        desc_templates = {
            "pt": f"{serie_nome} | DARK STUDIO AAA. {cta} 🔔 {hashtags}",
            "en": f"{serie_nome} | DARK STUDIO AAA. {cta} 🔔 {hashtags}",
            "es": f"{serie_nome} | DARK STUDIO AAA. {cta} 🔔 {hashtags}",
            "de": f"{serie_nome} | DARK STUDIO AAA. {cta} 🔔 {hashtags}",
            "fr": f"{serie_nome} | DARK STUDIO AAA. {cta} 🔔 {hashtags}",
            "ja": f"{serie_nome} | DARK STUDIO AAA。{cta} 🔔 {hashtags}",
            "ar": f"{serie_nome} | DARK STUDIO AAA. {cta} 🔔 {hashtags}",
        }

        return desc_templates.get(idioma, desc_templates.get("en", f"{serie_nome} | {cta}"))

    def prepare(
        self,
        canal: str,
        idioma: str,
        episodio: int = 1,
        script_override: Optional[str] = None,
    ) -> ProductionResult:
        """
        AGENTE: CINEMATIC DIRECTOR + AUDIO MASTER (preparação)

        Prepara todos os parâmetros para produção de um Short multilingual.
        NÃO executa chamadas de API — apenas monta o plano de produção.

        Args:
            canal: Nome do canal (chave em FACTORY_CONFIG)
            idioma: Código do idioma (en, es, de, fr, etc.)
            episodio: Número do episódio
            script_override: Script personalizado (se None, usa pré-escrito)

        Returns:
            ProductionResult com todos os parâmetros prontos
        """
        cfg = FACTORY_CONFIG.get(canal)
        if not cfg:
            raise ValueError(f"Canal não configurado: {canal}. Use: {list(FACTORY_CONFIG.keys())}")

        if idioma not in (cfg.get("idiomas_alvo", []) + [cfg.get("idioma_base", "pt")]):
            raise ValueError(f"Idioma {idioma} não configurado para {canal}")

        nicho = cfg["nicho"]
        serie_nome = cfg["series"].get(idioma, cfg["serie_pt"])
        cta = cfg["cta"].get(idioma, cfg["cta"].get("en", ""))
        voz_edge = self.VOZES.get(idioma, "en-US-AriaNeural")

        script = script_override or self._get_script(nicho, idioma, episodio)
        titulo = self._build_title(canal, idioma, episodio, nicho)
        descricao = self._build_description(canal, idioma, serie_nome, cta, nicho)

        estilo = ESTILOS_VISUAIS.get(nicho, ESTILOS_VISUAIS["horror"])
        hashtags = HASHTAGS.get(nicho, {}).get(idioma, f"#{serie_nome.replace(' ', '')}")

        tags_base = {
            "horror": ["horror", "mystery", "paranormal", "scary", "dark studio"],
            "motivacional": ["mental strength", "mindset", "discipline", "motivation", "psychology"],
            "tecnologia": ["technology", "AI", "science", "future", "innovation"],
            "relaxamento": ["relaxation", "nature", "meditation", "peace", "zen"],
            "historia": ["history", "mystery", "secret", "conspiracy", "hidden truth"],
            "misterio": ["mystery", "conspiracy", "secret", "investigation", "dark"],
        }
        tags = tags_base.get(nicho, ["dark studio", "shorts"])
        tags.extend([serie_nome.lower(), canal.lower(), f"dark studio {idioma}"])

        ai_disclosure_map = {
            "pt": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            "en": "Produced with DARK STUDIO AAA — DARK CREATIVE LAB",
            "es": "Producido con DARK STUDIO AAA — DARK CREATIVE LAB",
            "de": "Produziert mit DARK STUDIO AAA — DARK CREATIVE LAB",
            "fr": "Produit avec DARK STUDIO AAA — DARK CREATIVE LAB",
            "it": "Prodotto con DARK STUDIO AAA — DARK CREATIVE LAB",
            "ar": "تم الإنتاج مع DARK STUDIO AAA — DARK CREATIVE LAB",
            "ja": "DARK STUDIO AAA — DARK CREATIVE LABで制作",
            "zh": "由DARK STUDIO AAA — DARK CREATIVE LAB制作",
            "ko": "DARK STUDIO AAA — DARK CREATIVE LAB에서 제작",
            "pl": "Wyprodukowano w DARK STUDIO AAA — DARK CREATIVE LAB",
        }

        return ProductionResult(
            canal=canal,
            idioma=idioma,
            nicho=nicho,
            serie_nome=serie_nome,
            episodio=episodio,
            titulo=titulo,
            descricao=descricao,
            tags=tags,
            script=script,
            voz_edge=voz_edge,
            thumbnail_style=estilo["thumbnail_style"],
            video_prompt=estilo["video_prompt"],
            cta=cta,
            hashtags=hashtags,
            ai_disclosure=ai_disclosure_map.get(idioma, ai_disclosure_map["en"]),
        )

    def batch_week(self, semana: int = 1) -> List[ProductionResult]:
        """
        Prepara plano de produção completo para a semana.

        Retorna lista de ProductionResult para todos os idiomas configurados.
        Pode ser usado para preparar upload batch via vidIQ.
        """
        plano = []
        ep_base = (semana - 1) * 10 + 1

        combinacoes = [
            # (canal, idioma, episodio)
            ("Esquina do Medo", "en", ep_base),
            ("Esquina do Medo", "es", ep_base),
            ("Esquina do Medo", "de", ep_base),
            ("Mente de Aço", "en", ep_base),
            ("Mente de Aço", "fr", ep_base),
            ("Intelligentia Nova", "de", ep_base),
            ("AquaZen Relax", "en", ep_base),
            ("Bastidores do Tempo", "en", ep_base),
        ]

        for canal, idioma, ep in combinacoes:
            try:
                result = self.prepare(canal, idioma, ep)
                plano.append(result)
            except ValueError as e:
                print(f"⚠️  Skipping {canal}/{idioma}: {e}")

        return plano

    def export_production_brief(self, result: ProductionResult, output_path: Optional[str] = None) -> str:
        """Exporta brief de produção em JSON para uso pelos trigger prompts."""
        path = output_path or str(self.output_dir / f"brief_{result.canal.replace(' ','_')}_{result.idioma}_ep{result.episodio}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        return path

    def status(self) -> Dict[str, Any]:
        """Retorna status da factory e configurações."""
        total_combinacoes = sum(
            len(cfg.get("idiomas_alvo", []))
            for cfg in FACTORY_CONFIG.values()
        )
        return {
            "factory": "DARK_MULTILINGUAL_FACTORY",
            "versao": self.VERSION,
            "canais_configurados": len(FACTORY_CONFIG),
            "total_combinacoes_idioma": total_combinacoes,
            "idiomas_com_scripts": list(set(
                lang
                for nicho_scripts in SCRIPTS.values()
                for lang in nicho_scripts.keys()
            )),
            "nichos_disponíveis": list(SCRIPTS.keys()),
            "custo_tts": "GRATUITO (DarkEdgeTTS v2 cascade)",
            "custo_traducao": "GRATUITO (pré-escrito por idioma)",
            "ai_generated": True,
        }


# ─────────────────────────────────────────────────────────────────
# INTERFACE DE LINHA DE COMANDO
# ─────────────────────────────────────────────────────────────────

def _test_factory():
    """Testa a factory com combinações representativas."""
    factory = DarkMultilingualFactory()

    print("=" * 60)
    print("DARK MULTILINGUAL FACTORY — TESTE DE PRODUÇÃO")
    print("=" * 60)

    st = factory.status()
    for k, v in st.items():
        print(f"  {k}: {v}")
    print()

    testes = [
        ("Esquina do Medo", "en", 1),
        ("Esquina do Medo", "de", 2),
        ("Mente de Aço", "fr", 1),
        ("AquaZen Relax", "ja", 1),
        ("Bastidores do Tempo", "en", 1),
        ("Intelligentia Nova", "de", 1),
    ]

    for canal, idioma, ep in testes:
        print(f"{'─' * 50}")
        print(f"Canal: {canal} | Idioma: {idioma} | Ep: {ep}")
        try:
            result = factory.prepare(canal, idioma, ep)
            print(f"  Série: {result.serie_nome}")
            print(f"  Título: {result.titulo}")
            print(f"  Voz Edge: {result.voz_edge}")
            print(f"  Script: {result.script[:80]}...")
            print(f"  CTA: {result.cta[:60]}...")
            print(f"  Tags: {', '.join(result.tags[:5])}")
            print(f"  Status: ✅ OK")
        except Exception as e:
            print(f"  Status: ❌ ERRO: {e}")

    print(f"\n{'=' * 60}")
    print(f"✅ FACTORY TEST COMPLETE")
    print(f"   Combinações disponíveis: {sum(len(c.get('idiomas_alvo',[])) for c in FACTORY_CONFIG.values())}")
    print(f"   Scripts pré-escritos: {sum(len(s) for nicho in SCRIPTS.values() for s in nicho.values())} scripts")
    print(f"   Idiomas com scripts: {set(lang for nicho in SCRIPTS.values() for lang in nicho.keys())}")


if __name__ == "__main__":
    _test_factory()
