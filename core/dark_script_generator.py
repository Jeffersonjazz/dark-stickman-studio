"""
DARK SCRIPT GENERATOR â Agente de GeraÃ§Ã£o de Roteiros
======================================================
Banco com 30 tÃ³picos de dark histÃ³ria + gerador automÃ¡tico de roteiros.

Usado pelo DARK SHORTS FACTORY para selecionar o prÃ³ximo tema a produzir,
evitando repetiÃ§Ã£o e garantindo variedade de conteÃºdo.

Cada tÃ³pico contÃ©m:
  - titulo: tÃ­tulo chamativo para o Short
  - tema: identificador Ãºnico para controle de repetiÃ§Ã£o
  - roteiro: script completo narrado em PT-BR (400â650 chars)
  - hook: primeira frase impactante (3s)
  - tags: tags YouTube otimizadas
  - nicho: historia|misterio|documentario|tecnologia
  - semana_sugerida: rotaÃ§Ã£o semanal (1â52)

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA â DARK CREATIVE LAB
"""

from __future__ import annotations
import json
import random
from pathlib import Path
from typing import Optional

# Banco de tÃ³picos produzidos (evitar repetiÃ§Ã£o)
_LOG_PRODUZIDOS_PATH = Path(__file__).parent.parent / "db" / "topicos_produzidos.json"


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
#  BANCO DE 30 TÃPICOS â DARK HISTÃRIA
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

TOPICOS = [
    # ââ JÃ PRODUZIDOS âââââââââââââââââââââââââââââââââââââââââââââ
    {
        "tema": "mkultra",
        "titulo": "O Projeto MKUltra: A CIA Drogou Americanos Sem Consentimento",
        "nicho": "historia",
        "produzido": True,
        "youtube_url": "https://www.youtube.com/watch?v=v14e9_ms8lY",
        "data": "2026-11-12",
        "hook": "Em 1953, o governo americano experimentou drogas em cidadÃ£os comuns... sem que soubessem.",
        "roteiro": """Em 1953, o governo americano experimentou drogas em cidadÃ£os comuns... sem que soubessem.

O Projeto MKUltra foi um programa secreto da CIA que durou vinte anos. Cientistas testaram LSD, hipnose e tortura psicolÃ³gica em presos, pacientes psiquiÃ¡tricos e soldados â sem qualquer consentimento.

O objetivo era criar um mÃ©todo de controle mental. Um agente duplo que nÃ£o pudesse mentir. Uma arma invisÃ­vel.

Um dos sujeitos, o cientista Frank Olson, morreu misteriosamente apÃ³s receber LSD em sua bebida sem saber. Classificado como suicÃ­dio â por dÃ©cadas.

Em 1977, o Senado americano revelou a verdade. A CIA havia destruÃ­do quase todos os documentos em 1973. Mas os fragmentos que sobreviveram mudaram a histÃ³ria para sempre.

O que mais ainda Ã© segredo?""",
        "tags": ["MKUltra", "CIA", "histÃ³ria sombria", "documentÃ¡rio", "casos reais", "dark histÃ³ria"],
    },

    # ââ FILA DE PRODUÃÃO ââââââââââââââââââââââââââââââââââââââââââ
    {
        "tema": "paperclip",
        "titulo": "OperaÃ§Ã£o Paperclip: Os Nazistas Que a AmÃ©rica Contratou",
        "nicho": "historia",
        "produzido": True,
        "youtube_url": "https://www.youtube.com/watch?v=tgjgscDGFwo",
        "data": "2026-11-12",
        "hook": "ApÃ³s a Segunda Guerra, os EUA nÃ£o prenderam os cientistas nazistas. Os contrataram.",
        "roteiro": """ApÃ³s a Segunda Guerra, os EUA nÃ£o prenderam os cientistas nazistas. Os contrataram.

A OperaÃ§Ã£o Paperclip foi um programa secreto do governo americano que recrutou mais de 1.600 cientistas e engenheiros da Alemanha nazista entre 1945 e 1959.

Wernher von Braun, que projetou os mÃ­sseis V-2 usados contra civis britÃ¢nicos, tornou-se o arquiteto do programa espacial americano. Ele ajudou a levar o homem Ã  Lua.

Outros cientistas trouxeram pesquisas sobre medicina, aeronÃ¡utica e armas quÃ­micas â muitas realizadas em campos de concentraÃ§Ã£o com prisioneiros.

O governo americano apagou e alterou registros para ocultar os passados nazistas desses homens.

Alguns deles receberam medalhas americanas. Outros foram enterrados com honras militares.

A ciÃªncia que nos levou ao espaÃ§o tem um passado que ninguÃ©m conta nas escolas.""",
        "tags": ["OperaÃ§Ã£o Paperclip", "nazistas", "NASA", "Segunda Guerra", "histÃ³ria proibida", "dark histÃ³ria"],
    },
    {
        "tema": "tuskegee",
        "titulo": "Tuskegee: 40 Anos Deixando Negros Morrerem de SÃ­filis",
        "nicho": "historia",
        "produzido": False,
        "hook": "Por 40 anos, o governo americano observou 399 homens negros morrerem de sÃ­filis sem tratamento.",
        "roteiro": """Por 40 anos, o governo americano observou 399 homens negros morrerem de sÃ­filis sem tratamento.

O Estudo Tuskegee comeÃ§ou em 1932 no Alabama. O ServiÃ§o de SaÃºde PÃºblica dos EUA recrutou homens negros pobres com sÃ­filis, prometendo tratamento gratuito.

O que eles receberam foi placebos. Aspirina. Vitaminas. Nada que curasse a doenÃ§a.

Quando a penicilina foi descoberta em 1947 â uma cura para sÃ­filis â o estudo continuou. Os pesquisadores nÃ£o queriam perder seus sujeitos de teste.

Os homens nÃ£o foram informados de que tinham sÃ­filis. Foram chamados de "sangue ruim".

O estudo durou atÃ© 1972, quando um denunciante vazou os documentos para a imprensa.

Nenhum mÃ©dico foi processado.

Em 1997, o presidente Clinton pediu desculpas aos sobreviventes. Apenas oito estavam vivos para ouvir.""",
        "tags": ["Tuskegee", "experimento sÃ­filis", "racismo mÃ©dico", "EUA", "histÃ³ria sombria", "dark histÃ³ria"],
    },
    {
        "tema": "unit731",
        "titulo": "Unidade 731: Os Experimentos Japoneses Que Chocaram o Mundo",
        "nicho": "historia",
        "produzido": False,
        "hook": "Numa base secreta na ManchÃºria, mÃ©dicos japoneses realizaram experimentos que a humanidade tentou esquecer.",
        "roteiro": """Numa base secreta na ManchÃºria, mÃ©dicos japoneses realizaram experimentos que a humanidade tentou esquecer.

A Unidade 731 foi uma divisÃ£o de pesquisa de armas biolÃ³gicas do ExÃ©rcito Imperial JaponÃªs ativa entre 1935 e 1945. Estima-se que 3.000 a 300.000 pessoas morreram em seus laboratÃ³rios.

Prisioneiros â chamados de "toras", pedaÃ§os de madeira â foram infectados com cÃ³lera, tifo e peste. Foram operados sem anestesia. Foram congelados vivos para testar os limites do organismo humano.

Ao fim da guerra, os EUA fecharam um acordo secreto com o General ShirÅ Ishii: imunidade total por todos os dados de experimentos.

Nenhum membro da Unidade 731 foi julgado em Nuremberg.

ShirÅ Ishii morreu de cÃ¢ncer de garganta em 1959, em paz, em TÃ³quio.

Os dados desses experimentos ainda existem. Alguns foram usados por laboratÃ³rios americanos.""",
        "tags": ["Unidade 731", "Segunda Guerra", "JapÃ£o", "experimentos", "crimes de guerra", "dark histÃ³ria"],
    },
    {
        "tema": "cointelpro",
        "titulo": "COINTELPRO: O FBI Espionou e Destruiu Movimentos Negros",
        "nicho": "historia",
        "produzido": False,
        "hook": "Nos anos 60, o FBI tinha um programa secreto para destruir lÃ­deres negros americanos.",
        "roteiro": """Nos anos 60, o FBI tinha um programa secreto para destruir lÃ­deres negros americanos.

O COINTELPRO â Programa de Contra-InteligÃªncia â foi operado pelo FBI entre 1956 e 1971. Seu objetivo declarado: "neutralizar" organizaÃ§Ãµes polÃ­ticas consideradas ameaÃ§as.

Mas na prÃ¡tica, isso significou infiltrar organizaÃ§Ãµes negras, criar divisÃµes entre lÃ­deres, forjar cartas e documentos, e coordenar prisÃµes falsas.

Martin Luther King recebeu uma carta anÃ´nima do FBI sugerindo que se suicidasse. A carta vazou dÃ©cadas depois.

Fred Hampton, lÃ­der dos Panteras Negras de 21 anos, foi assassinado durante uma operaÃ§Ã£o policial coordenada com o FBI em 1969. Ele dormia quando foi morto.

Em 1971, ativistas roubaram documentos de um escritÃ³rio do FBI e enviaram para a imprensa. O COINTELPRO foi exposto.

O FBI nunca pediu desculpas.""",
        "tags": ["COINTELPRO", "FBI", "Martin Luther King", "Panteras Negras", "histÃ³ria americana", "dark histÃ³ria"],
    },
    {
        "tema": "sarin_tokyo",
        "titulo": "O Ataque de Sarin no MetrÃ´ de TÃ³quio",
        "nicho": "misterio",
        "produzido": False,
        "hook": "Em 1995, membros de um culto liberaram gÃ¡s sarin no metrÃ´ mais movimentado do mundo.",
        "roteiro": """Em 1995, membros de um culto religioso liberaram gÃ¡s sarin no metrÃ´ mais movimentado do mundo.

Era uma manhÃ£ comum em TÃ³quio. Dezenas de passageiros comeÃ§aram a convulsionar nas plataformas. Treze pessoas morreram. Mais de 50 ficaram permanentemente feridas. Mais de 1.000 sofreram danos visuais duradouros.

O culto Aum Shinrikyo era liderado por Shoko Asahara, que se dizia o Cristo japonÃªs e pregava o Apocalipse. Seus membros incluÃ­am cientistas, mÃ©dicos e engenheiros.

Eles tinham planos para criar armas biolÃ³gicas, comprar tanques e atÃ© uma mina de urÃ¢nio na AustrÃ¡lia.

O ataque foi planejado para distrair a polÃ­cia que investigava o grupo.

Asahara foi executado em 2018.

Mas o que mais assustou o mundo: o culto tinha mais de 50.000 membros no JapÃ£o â e 30.000 na RÃºssia.""",
        "tags": ["Aum Shinrikyo", "sarin", "TÃ³quio", "culto", "ataque terrorista", "dark histÃ³ria"],
    },
    {
        "tema": "jonestown",
        "titulo": "Jonestown: O Dia em Que 918 Pessoas Beberam Veneno",
        "nicho": "misterio",
        "produzido": False,
        "hook": "Em 18 de novembro de 1978, 918 pessoas morreram em 45 minutos na selva da Guiana.",
        "roteiro": """Em 18 de novembro de 1978, 918 pessoas morreram em 45 minutos na selva da Guiana.

Jim Jones era um pastor americano carismÃ¡tico que prometia igualdade racial, comunidade e proteÃ§Ã£o. Milhares o seguiram atÃ© uma colÃ´nia na Guiana chamada Jonestown.

Mas o paraÃ­so era uma prisÃ£o. Membros que tentavam sair eram punidos. CrianÃ§as eram usadas como refÃ©ns. Jones ouvia tudo por microfones escondidos.

Quando um congressista americano chegou para investigar denÃºncias, Jones ordenou que sua equipe fosse assassinada na pista de pouso.

Depois, ele anunciou o "suicÃ­dio revolucionÃ¡rio".

Uma bebida de Kool-Aid misturada com cianeto foi distribuÃ­da. CrianÃ§as beberam primeiro. Pais deram aos filhos. Guardas atiraram em quem se recusava.

Foi o maior assassinato em massa de civis americanos antes do 11 de setembro.""",
        "tags": ["Jonestown", "Jim Jones", "culto", "suicÃ­dio em massa", "Guiana", "dark histÃ³ria"],
    },
    {
        "tema": "radium_girls",
        "titulo": "As Radium Girls: Mulheres Que Pintavam RelÃ³gios Com Veneno",
        "nicho": "historia",
        "produzido": False,
        "hook": "Nos anos 20, centenas de jovens pintavam relÃ³gios com rÃ¡dio radioativo â e eram incentivadas a lamber o pincel.",
        "roteiro": """Nos anos 20, centenas de jovens pintavam relÃ³gios com rÃ¡dio radioativo â e eram incentivadas a lamber o pincel para afiar a ponta.

Eram mulheres jovens nas fÃ¡bricas de relÃ³gios dos EUA. O rÃ¡dio brilhava no escuro, e elas eram instruÃ­das a usar a tÃ©cnica "lip, dip, paint" â lamber, mergulhar, pintar.

Algumas pintavam os dentes e unhas para brilhar na saÃ­da.

Elas nÃ£o sabiam que o rÃ¡dio causava cÃ¢ncer de osso. As empresas sabiam.

Quando suas mandÃ­bulas comeÃ§aram a se dissolver e seus ossos a quebrar espontaneamente, as empresas disseram que elas estavam com sÃ­filis.

Um grupo de mulheres processou a empresa. Os documentos internos revelaram que a empresa sabia dos riscos desde 1920.

Elas venceram â mas a maioria morreu antes de ver o resultado.

Suas histÃ³rias foram suprimidas por dÃ©cadas. Hoje, seus corpos ainda emitem radiaÃ§Ã£o.""",
        "tags": ["Radium Girls", "rÃ¡dio", "radiaÃ§Ã£o", "histÃ³ria feminina", "capitalismo", "dark histÃ³ria"],
    },
    {
        "tema": "agent_orange",
        "titulo": "Agente Laranja: O Veneno Que Os EUA Despejaram no VietnÃ£",
        "nicho": "historia",
        "produzido": False,
        "hook": "Entre 1961 e 1971, os EUA despejaram 77 milhÃµes de litros de herbicida tÃ³xico sobre populaÃ§Ãµes civis.",
        "roteiro": """Entre 1961 e 1971, os EUA despejaram 77 milhÃµes de litros de herbicida tÃ³xico sobre populaÃ§Ãµes civis no VietnÃ£.

O Agente Laranja continha dioxina â um dos compostos mais tÃ³xicos jÃ¡ criados pelo homem.

O objetivo era destruir a cobertura vegetal e as plantaÃ§Ãµes vietnamitas. O resultado foi catastrÃ³fico para geraÃ§Ãµes.

Estima-se que 400.000 pessoas morreram ou ficaram com deficiÃªncias. 500.000 crianÃ§as nasceram com malformaÃ§Ãµes congÃªnitas. Os efeitos persistiram por quatro geraÃ§Ãµes.

Os fabricantes â incluindo a Dow Chemical e a Monsanto â sabiam dos riscos da dioxina desde os anos 1950.

Veteranos americanos tambÃ©m foram afetados. Levaram dÃ©cadas para serem reconhecidos e indenizados.

O VietnÃ£ ainda pede reparaÃ§Ãµes. Os EUA ainda nÃ£o as pagaram.

As Ãºltimas anÃ¡lises de solo em antigas bases americanas ainda registram nÃ­veis perigosos de contaminaÃ§Ã£o.""",
        "tags": ["Agente Laranja", "VietnÃ£", "guerra quÃ­mica", "dioxina", "EUA", "dark histÃ³ria"],
    },
    {
        "tema": "mk_naomi",
        "titulo": "Projeto MK-NAOMI: Armas BiolÃ³gicas Testadas em Soldados",
        "nicho": "historia",
        "produzido": False,
        "hook": "Paralelo ao MKUltra, a CIA tinha outro programa secreto: armas biolÃ³gicas testadas em soldados americanos.",
        "roteiro": """Paralelo ao MKUltra, a CIA tinha outro programa secreto: armas biolÃ³gicas testadas em soldados americanos.

O Projeto MK-NAOMI foi operado entre 1952 e 1970. Seu objetivo: desenvolver agentes patogÃªnicos que causassem doenÃ§as ou morte sem deixar traÃ§os.

Cientistas da CIA e do ExÃ©rcito desenvolveram toxinas, vÃ­rus e bactÃ©rias para uso em campo. Testaram esses agentes em soldados sem seu consentimento.

Em 1951, moradores de San Francisco foram expostos a bactÃ©rias liberadas da baÃ­a por navios da Marinha americana â como parte de um teste secreto de dispersÃ£o.

Pelo menos um homem morreu. O governo negou por dÃ©cadas.

Documentos desclassificados revelaram mais de 200 testes urbanos em cidades americanas entre 1949 e 1969.

New York, St. Louis, Minneapolis â todas foram usadas como laboratÃ³rios secretos.

Nenhum lÃ­der do programa foi processado.""",
        "tags": ["MK-NAOMI", "CIA", "armas biolÃ³gicas", "experimentos militares", "San Francisco", "dark histÃ³ria"],
    },
    {
        "tema": "operation_northwoods",
        "titulo": "OperaÃ§Ã£o Northwoods: O Plano Para Culpar Cuba Por Atentados Falsos",
        "nicho": "historia",
        "produzido": False,
        "hook": "Em 1962, o Estado-Maior americano propÃ´s realizar ataques terroristas nos EUA e culpar Cuba.",
        "roteiro": """Em 1962, o Estado-Maior americano propÃ´s realizar ataques terroristas nos EUA e culpar Cuba para justificar uma invasÃ£o.

O plano era chamado de OperaÃ§Ã£o Northwoods. O documento foi classificado por dÃ©cadas.

As propostas incluÃ­am: simular ataque a base americana em GuantÃ¢namo, criar vÃ­timas falsas, afundar barcos refugiados cubanos, bombardear Miami, e derrubar um aviÃ£o com estudantes americanos â substituindo os passageiros reais por impostores.

O objetivo: criar pretexto para declarar guerra a Cuba.

John F. Kennedy recusou o plano. Poucos meses depois, foi assassinado.

O documento foi desclassificado em 1997. EstÃ¡ disponÃ­vel nos Arquivos Nacionais dos EUA.

NÃ£o Ã© teoria da conspiraÃ§Ã£o. Ã histÃ³ria.""",
        "tags": ["OperaÃ§Ã£o Northwoods", "Cuba", "JFK", "Estado-Maior", "false flag", "dark histÃ³ria"],
    },
    {
        "tema": "pueblo_chile",
        "titulo": "O Golpe No Chile: A CIA Derrubou Uma Democracia",
        "nicho": "historia",
        "produzido": False,
        "hook": "Em 1973, a CIA coordenou o golpe que derrubou o presidente democraticamente eleito do Chile.",
        "roteiro": """Em 1973, a CIA coordenou o golpe que derrubou o presidente democraticamente eleito do Chile.

Salvador Allende foi eleito em 1970 com um programa socialista. Os EUA consideraram isso inaceitÃ¡vel.

A CIA gastou milhÃµes para desestabilizar a economia chilena, financiar greves e apoiar grupos de oposiÃ§Ã£o.

Em 11 de setembro de 1973, militares atacaram o PalÃ¡cio de La Moneda. Allende morreu â seja por suicÃ­dio, seja assassinado â enquanto o palÃ¡cio era bombardeado.

A ditadura de Pinochet durou 17 anos. Mais de 3.200 pessoas foram mortas ou desaparecidas. 40.000 foram torturadas.

Henry Kissinger, SecretÃ¡rio de Estado americano, disse na Ã©poca: "NÃ£o posso ver por que devemos ficar de braÃ§os cruzados enquanto um paÃ­s se torna comunista pela irresponsabilidade do seu prÃ³prio povo."

Em 2023, documentos desclassificados confirmaram o envolvimento direto da CIA.

A democracia foi um efeito colateral que os EUA nÃ£o toleraram.""",
        "tags": ["Chile", "Allende", "Pinochet", "CIA", "golpe de estado", "dark histÃ³ria"],
    },
    {
        "tema": "amistad_syphilis",
        "titulo": "Guatemala 1946: EUA Infectaram Propositalmente PresidiÃ¡rios Com SÃ­filis",
        "nicho": "historia",
        "produzido": False,
        "hook": "Na Guatemala, mÃ©dicos americanos infectaram deliberadamente presidiÃ¡rios, soldados e pacientes psiquiÃ¡tricos com sÃ­filis.",
        "roteiro": """Na Guatemala, entre 1946 e 1948, mÃ©dicos americanos infectaram deliberadamente presidiÃ¡rios, soldados e pacientes psiquiÃ¡tricos com sÃ­filis e gonorreia.

Sem consentimento. Sem informaÃ§Ã£o. Apenas como experimento.

O projeto era financiado pelo governo americano e conduzido pelo mesmo pesquisador responsÃ¡vel pelo Estudo Tuskegee.

Mais de 1.300 guatemaltecos foram infectados. 83 morreram durante o estudo.

O projeto permaneceu secreto por mais de 60 anos. Foi descoberto por uma pesquisadora americana em 2010.

A presidente Barack Obama telefonou para o presidente da Guatemala para se desculpar.

Nenhum mÃ©dico foi processado.

Nenhuma indenizaÃ§Ã£o foi paga Ã s vÃ­timas ou Ã s suas famÃ­lias.

Isso aconteceu apenas um ano depois do julgamento de Nuremberg, que condenou mÃ©dicos nazistas por experimentos similares.""",
        "tags": ["Guatemala", "sÃ­filis", "experimento mÃ©dico", "EUA", "crimes mÃ©dicos", "dark histÃ³ria"],
    },
    {
        "tema": "fluoride",
        "titulo": "A Verdade Sobre o FlÃºor: Por Que Ele Foi Colocado na Ãgua",
        "nicho": "historia",
        "produzido": False,
        "hook": "A histÃ³ria da fluoretaÃ§Ã£o da Ã¡gua americana comeÃ§a nÃ£o em pesquisa dentÃ¡ria, mas em indÃºstrias de alumÃ­nio.",
        "roteiro": """A histÃ³ria da fluoretaÃ§Ã£o da Ã¡gua americana comeÃ§a nÃ£o em pesquisa dentÃ¡ria, mas em indÃºstrias de alumÃ­nio.

No final dos anos 1940, a Alcoa e outras indÃºstrias tinham um problema: fluoreto era subproduto tÃ³xico de seus processos e caro para descartar.

Estudos cientÃ­ficos da Ã©poca mostravam benefÃ­cios do flÃºor para dentes em pequenas doses. Isso foi usado como justificativa.

Em 1945, Grand Rapids, Michigan, se tornou a primeira cidade a flurorar a Ã¡gua â sem estudos de longo prazo sobre seguranÃ§a.

Documentos desclassificados revelaram que cientistas do Projeto Manhattan estavam preocupados com processos legais relacionados ao flÃºor â e apoiaram publicamente a fluoretaÃ§Ã£o como estratÃ©gia de relaÃ§Ãµes pÃºblicas.

Hoje, 60% das cidades americanas ainda fluroram a Ã¡gua.

A maioria dos paÃ­ses europeus nÃ£o fluoreta a Ã¡gua.

Isso nÃ£o Ã© conspiracy theory. Ã histÃ³ria industrial que moldou polÃ­tica pÃºblica.""",
        "tags": ["flÃºor", "fluoretaÃ§Ã£o", "Ã¡gua", "indÃºstria quÃ­mica", "Projeto Manhattan", "dark histÃ³ria"],
    },
    {
        "tema": "mk_ultra_canada",
        "titulo": "O CanadÃ¡ TambÃ©m Tinha MKUltra: Dr. Ewen Cameron e a DesprogramaÃ§Ã£o",
        "nicho": "historia",
        "produzido": False,
        "hook": "O maior hospital psiquiÃ¡trico do CanadÃ¡ foi palco de um dos experimentos mais cruÃ©is financiados pela CIA.",
        "roteiro": """O maior hospital psiquiÃ¡trico do CanadÃ¡ foi palco de um dos experimentos mais cruÃ©is financiados pela CIA.

O Dr. Ewen Cameron acreditava que podia "desprogramar" a mente humana e reconstruÃ­-la do zero.

No Instituto Allan Memorial em Montreal, entre 1957 e 1964, pacientes eram mantidos em sono induzido por semanas. Recebiam doses massivas de LSD e barbitÃºricos. Eram submetidos a sessÃµes de eletroconvulsoterapia atÃ© 150 vezes seguidas â quando o padrÃ£o mÃ©dico era 20.

Algumas sessÃµes duravam dias. Pacientes ouvia mensagens em loop enquanto dormiam, numa tÃ©cnica chamada "psydriving".

Muitos foram destruÃ­dos. Perderam memÃ³rias. Esqueceram seus filhos. Regrediram Ã  infÃ¢ncia.

A maioria tinha entrado voluntariamente para tratar ansiedade ou depressÃ£o leve.

A CIA financiou o projeto. O governo canadense tambÃ©m contribuiu.

Em 1988, o governo canadense pagou indenizaÃ§Ãµes Ã s vÃ­timas. Sem reconhecer culpa.""",
        "tags": ["Ewen Cameron", "Montreal", "CIA", "MKUltra", "psiquiatria", "dark histÃ³ria"],
    },

    # ââ TÃPICOS FUTUROS âââââââââââââââââââââââââââââââââââââââââââ
    {
        "tema": "bhopal",
        "titulo": "Bhopal 1984: O Maior Desastre Industrial da HistÃ³ria",
        "nicho": "historia",
        "produzido": False,
        "hook": "Na madrugada de 3 de dezembro de 1984, nuvem tÃ³xica matou mais de 15.000 pessoas enquanto dormiam.",
        "roteiro": "",  # A ser gerado
        "tags": ["Bhopal", "Union Carbide", "India", "desastre industrial", "dark histÃ³ria"],
    },
    {
        "tema": "mk_search",
        "titulo": "MK-SEARCH: O Projeto Que Testou Drogas em CrianÃ§as ÃrfÃ£s",
        "nicho": "historia",
        "produzido": False,
        "hook": "O sucessor do MKUltra testou drogas em crianÃ§as sem famÃ­lia e sem advogado.",
        "roteiro": "",
        "tags": ["MK-SEARCH", "CIA", "crianÃ§as", "experimentos", "dark histÃ³ria"],
    },
    {
        "tema": "operation_paperclip_bioweapons",
        "titulo": "Fort Detrick: A Base Americana De Armas BiolÃ³gicas",
        "nicho": "historia",
        "produzido": False,
        "hook": "Na Maryland, o exÃ©rcito americano manteve por dÃ©cadas um programa de armas biolÃ³gicas â com cientistas nazistas.",
        "roteiro": "",
        "tags": ["Fort Detrick", "armas biolÃ³gicas", "nazistas", "EUA", "dark histÃ³ria"],
    },
    {
        "tema": "stanford_prison",
        "titulo": "O Experimento da PrisÃ£o de Stanford: Quando Estudantes Viraram Monstros",
        "nicho": "misterio",
        "produzido": False,
        "hook": "Em 1971, estudantes universitÃ¡rios foram divididos em prisioneiros e guardas. Em 6 dias, foi um inferno.",
        "roteiro": "",
        "tags": ["Experimento Stanford", "psicologia", "Philip Zimbardo", "dark histÃ³ria"],
    },
    {
        "tema": "guatemala_syphilis_complete",
        "titulo": "O MÃ©dico Que Infectou CrianÃ§as Com SÃ­filis Para Testar Penicilina",
        "nicho": "historia",
        "produzido": False,
        "hook": "John Cutler infectou pacientes psiquiÃ¡tricos guatemaltecos. Depois, foi o mesmo mÃ©dico do Tuskegee.",
        "roteiro": "",
        "tags": ["John Cutler", "Guatemala", "Tuskegee", "sÃ­filis", "dark histÃ³ria"],
    },
    {
        "tema": "tulsa_massacre",
        "titulo": "O Massacre de Tulsa: A Cidade Negra PrÃ³spera Que Foi DestruÃ­da",
        "nicho": "historia",
        "produzido": False,
        "hook": "Em 1921, Greenwood era chamada de 'Black Wall Street'. Em dois dias, foi varrida do mapa.",
        "roteiro": "",
        "tags": ["Tulsa", "Greenwood", "massacre racial", "Black Wall Street", "dark histÃ³ria"],
    },
    {
        "tema": "operation_paperclip_space",
        "titulo": "O Nazista Que Nos Levou Ã  Lua",
        "nicho": "historia",
        "produzido": False,
        "hook": "O homem responsÃ¡vel pelo programa Apollo usou trabalho escravo em fÃ¡bricas subterrÃ¢neas nazistas.",
        "roteiro": "",
        "tags": ["Wernher von Braun", "NASA", "nazismo", "Apollo", "dark histÃ³ria"],
    },
    {
        "tema": "atomic_veterans",
        "titulo": "Os Soldados Que Assistiram Testes Nucleares Sem ProteÃ§Ã£o",
        "nicho": "historia",
        "produzido": False,
        "hook": "Dezenas de milhares de soldados americanos foram ordenados a marchar para dentro da zona de explosÃ£o nuclear.",
        "roteiro": "",
        "tags": ["testes nucleares", "soldados", "radiaÃ§Ã£o", "Bikini Atoll", "dark histÃ³ria"],
    },
    {
        "tema": "mk_ultra_artists",
        "titulo": "A CIA Financiou Arte Abstrata Para Ganhar a Guerra Fria",
        "nicho": "historia",
        "produzido": False,
        "hook": "Jackson Pollock, Mark Rothko, o Abstract Expressionism â financiado secretamente pela CIA como arma cultural.",
        "roteiro": "",
        "tags": ["CIA", "arte abstrata", "Guerra Fria", "propaganda cultural", "dark histÃ³ria"],
    },
    {
        "tema": "church_committee",
        "titulo": "O ComitÃª Church: Quando o Senado Descobriu os Crimes da CIA",
        "nicho": "historia",
        "produzido": False,
        "hook": "Em 1975, investigadores do Senado abriram arquivos que revelaram dÃ©cadas de crimes da inteligÃªncia americana.",
        "roteiro": "",
        "tags": ["ComitÃª Church", "CIA", "FBI", "NSA", "dark histÃ³ria"],
    },
    {
        "tema": "radium_clock",
        "titulo": "O RelÃ³gio de RÃ¡dio: Por Que Tantas Casas Americanas Eram Radioativas",
        "nicho": "historia",
        "produzido": False,
        "hook": "Por dÃ©cadas, relÃ³gios radioativos foram vendidos como eletrodomÃ©sticos normais â e estavam nas casas de famÃ­lias americanas.",
        "roteiro": "",
        "tags": ["rÃ¡dio", "radiaÃ§Ã£o", "relÃ³gios", "contaminaÃ§Ã£o", "dark histÃ³ria"],
    },
    {
        "tema": "columbine_warning",
        "titulo": "O FBI Sabia Sobre Columbine e NÃ£o Fez Nada",
        "nicho": "misterio",
        "produzido": False,
        "hook": "Um ano antes do massacre de Columbine, um pai entregou ao FBI evidÃªncias e recebeu o caso de volta arquivado.",
        "roteiro": "",
        "tags": ["Columbine", "FBI", "escola", "EUA", "dark histÃ³ria"],
    },
    {
        "tema": "operation_mockingbird",
        "titulo": "OperaÃ§Ã£o Mockingbird: A CIA Controlava Os Jornalistas",
        "nicho": "historia",
        "produzido": False,
        "hook": "A CIA recrutou repÃ³rteres, editores e diretores de redes de TV para publicar histÃ³rias falsas.",
        "roteiro": "",
        "tags": ["OperaÃ§Ã£o Mockingbird", "CIA", "imprensa", "propaganda", "dark histÃ³ria"],
    },
    {
        "tema": "mk_delta",
        "titulo": "MK-DELTA: OperaÃ§Ãµes de Controle Mental No Exterior",
        "nicho": "historia",
        "produzido": False,
        "hook": "Enquanto o MKUltra funcionava nos EUA, a CIA testava tÃ©cnicas de controle mental em outros paÃ­ses.",
        "roteiro": "",
        "tags": ["MK-DELTA", "CIA", "operaÃ§Ã£o exterior", "controle mental", "dark histÃ³ria"],
    },
]


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
#  FUNÃÃES PRINCIPAIS
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def listar_topicos(apenas_pendentes: bool = True) -> list[dict]:
    """Retorna lista de tÃ³picos pendentes de produÃ§Ã£o."""
    if apenas_pendentes:
        return [t for t in TOPICOS if not t.get("produzido", False)]
    return TOPICOS


def proximo_topico(excluir_temas: list[str] = None) -> Optional[dict]:
    """Retorna o prÃ³ximo tÃ³pico a ser produzido (com roteiro completo)."""
    excluidos = set(excluir_temas or [])
    candidatos = [
        t for t in TOPICOS
        if not t.get("produzido", False)
        and t.get("roteiro", "").strip()  # SÃ³ com roteiro pronto
        and t["tema"] not in excluidos
    ]
    if not candidatos:
        return None
    return candidatos[0]


def topico_por_tema(tema: str) -> Optional[dict]:
    """Busca tÃ³pico especÃ­fico pelo identificador."""
    for t in TOPICOS:
        if t["tema"] == tema:
            return t
    return None


def marcar_produzido(tema: str, youtube_url: str, data: str = "") -> bool:
    """Registra tema como produzido (para evitar repetiÃ§Ã£o)."""
    import datetime
    _LOG_PRODUZIDOS_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Carregar log existente
    log = {}
    if _LOG_PRODUZIDOS_PATH.exists():
        try:
            log = json.loads(_LOG_PRODUZIDOS_PATH.read_text(encoding="utf-8"))
        except Exception:
            log = {}

    log[tema] = {
        "youtube_url": youtube_url,
        "data": data or datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d"),
    }
    _LOG_PRODUZIDOS_PATH.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    return True


def temas_ja_produzidos() -> list[str]:
    """Retorna lista de temas jÃ¡ produzidos (do log local + do banco)."""
    # Do banco embutido
    produzidos = [t["tema"] for t in TOPICOS if t.get("produzido", False)]

    # Do arquivo de log
    if _LOG_PRODUZIDOS_PATH.exists():
        try:
            log = json.loads(_LOG_PRODUZIDOS_PATH.read_text(encoding="utf-8"))
            produzidos.extend(log.keys())
        except Exception:
            pass

    return list(dict.fromkeys(produzidos))  # deduplica mantendo ordem


def gerar_roteiro_template(topico: dict) -> str:
    """Gera roteiro bÃ¡sico para tÃ³picos sem roteiro completo."""
    return (
        f"{topico['hook']}\n\n"
        f"[CENA 1 â Contexto histÃ³rico: {topico['titulo']}]\n\n"
        f"[CENA 2 â Desenvolvimento: Quem estava envolvido e o que aconteceu]\n\n"
        f"[CENA 3 â ClÃ­max: O momento mais impactante]\n\n"
        f"[CENA 4 â RevelaÃ§Ã£o: Quando e como a verdade veio Ã  tona]\n\n"
        f"[CENA 5 â Legado: O que ficou e o que ainda Ã© secreto]\n\n"
        f"O que mais ainda Ã© segredo?"
    )


def resumo_producao() -> dict:
    """Retorna resumo do status de produÃ§Ã£o do canal."""
    total = len(TOPICOS)
    produzidos = len([t for t in TOPICOS if t.get("produzido", False)])
    com_roteiro = len([t for t in TOPICOS if t.get("roteiro", "").strip()])
    pendentes = total - produzidos

    proximo = proximo_topico()

    return {
        "total_topicos": total,
        "produzidos": produzidos,
        "pendentes": pendentes,
        "com_roteiro_pronto": com_roteiro,
        "sem_roteiro": total - com_roteiro,
        "proximo_tema": proximo["tema"] if proximo else None,
        "proximo_titulo": proximo["titulo"] if proximo else None,
        "semanas_de_conteudo": pendentes,
        "meses_de_conteudo": round(pendentes / 4.3, 1),
    }


if __name__ == "__main__":
    r = resumo_producao()
    print("ð DARK SCRIPT GENERATOR â STATUS")
    print(f"   Total de tÃ³picos: {r['total_topicos']}")
    print(f"   â Produzidos: {r['produzidos']}")
    print(f"   ð Pendentes: {r['pendentes']}")
    print(f"   ð Com roteiro: {r['com_roteiro_pronto']}")
    print(f"   â³ Semanas de conteÃºdo: {r['semanas_de_conteudo']}")
    print(f"   ð Meses de conteÃºdo: {r['meses_de_conteudo']}")
    print(f"\nð¬ PrÃ³ximo tema: {r['proximo_titulo']}")
