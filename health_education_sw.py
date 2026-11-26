"""Kiswahili versions of the detailed health education guides.

Keys match DISEASES in health_education.py. Medicine names are kept in
their international form so they match what is written on packets and in
clinic records.
"""

DISEASES_SW = {
    "Malaria": {
        "name": "Malaria",
        "category": "Ugonjwa wa kuambukiza",
        "overview": (
            "Ugonjwa unaoweza kuua unaosababishwa na vimelea vya Plasmodium. Plasmodium falciparum, "
            "aina hatari zaidi, ndiyo inayopatikana zaidi Kenya. Watoto chini ya miaka 5 na "
            "wanawake wajawazito wako katika hatari kubwa zaidi."
        ),
        "causes": [
            "Kuumwa na mbu jike wa Anopheles aliyeambukizwa (hasa usiku)",
            "Mara chache: kuongezewa damu au kutoka kwa mama kwenda kwa mtoto",
            "Hatari kubwa zaidi maeneo ya ziwa, pwani na nyanda za chini, na wakati wa mvua",
        ],
        "symptoms": [
            "Homa, kutetemeka kwa baridi na kutokwa jasho",
            "Maumivu ya kichwa, maumivu ya mwili na uchovu",
            "Kichefuchefu, kutapika, kukosa hamu ya kula",
            "Malaria kali: kuchanganyikiwa, degedege, shida ya kupumua, mkojo mweusi, "
            "upungufu mkubwa wa damu, kushindwa kukaa au kunywa",
        ],
        "diagnosis": [
            "Kipimo cha haraka cha malaria (mRDT)",
            "Kipimo cha damu kwa hadubini",
            "Kila mtu anayeshukiwa kuwa na malaria apimwe kabla ya kutibiwa",
        ],
        "treatment": [
            "Malaria isiyo kali: dawa mseto za artemisinin (ACT), kama artemether-lumefantrine",
            "Malaria kali: sindano ya artesunate hospitalini, kisha dozi kamili ya ACT",
            "Huduma nyingine: kushusha homa, maji mwilini, na kutibu upungufu wa damu ukiwa mkubwa",
        ],
        "management": [
            "Maliza dozi yote ya dawa hata ukijisikia vizuri",
            "Lala ndani ya chandarua kilichotiwa dawa kila usiku",
            "Kunyunyizia dawa ndani ya nyumba na kuondoa maji yaliyotuama",
            "Dawa ya kinga wakati wa ujauzito (IPTp) kupitia kliniki ya wajawazito",
            "Chanjo ya malaria kwa watoto wadogo katika maeneo yanayostahili",
        ],
        "urgent": "Degedege, kuchanganyikiwa, usingizi mzito sana, kushindwa kunywa, au shida ya kupumua.",
    },
    "Tuberculosis (TB)": {
        "name": "Kifua kikuu (TB)",
        "category": "Ugonjwa wa kuambukiza",
        "overview": (
            "Maambukizi ya bakteria yanayoathiri zaidi mapafu lakini yanaweza kuathiri sehemu yoyote "
            "ya mwili. Kinatibika na kinazuilika."
        ),
        "causes": [
            "Bakteria Mycobacterium tuberculosis, husambaa hewani mtu mwenye TB ya mapafu "
            "anapokohoa, kupiga chafya au kuongea",
            "Hatari kubwa zaidi: VVU, kisukari, utapiamlo, uvutaji sigara, nyumba zenye msongamano "
            "au zisizo na hewa ya kutosha, kukaa karibu na mgonjwa wa TB",
        ],
        "symptoms": [
            "Kikohozi cha wiki 2 au zaidi, wakati mwingine chenye damu",
            "Homa na kutokwa jasho usiku",
            "Kupungua uzito na kukosa hamu ya kula",
            "Maumivu ya kifua na uchovu",
        ],
        "diagnosis": [
            "Kipimo cha makohozi cha kisasa (mf. GeneXpert), ambacho pia hugundua usugu wa rifampicin",
            "Kipimo cha makohozi kwa hadubini",
            "Picha ya X-ray ya kifua",
            "Kipimo cha VVU kwa kila mtu aliyegunduliwa na TB",
        ],
        "treatment": [
            "TB isiyo sugu: mchanganyiko wa antibiotiki kwa miezi 6 (rifampicin, isoniazid, "
            "pyrazinamide na ethambutol katika awamu ya kwanza)",
            "TB sugu: matibabu marefu zaidi au tofauti chini ya wataalamu",
            "Matibabu ni bure katika vituo vya afya vya umma Kenya",
        ],
        "management": [
            "Meza dawa kila siku hadi mwisho; msaada wa kumeza dawa (DOT) husaidia",
            "Wapime wanaoishi nyumba moja na mgonjwa na uwape dawa ya kinga wanapostahili",
            "Lishe bora na hewa safi nyumbani; funika mdomo unapokohoa",
            "Chanjo ya BCG kwa watoto wachanga",
        ],
        "urgent": "Kukohoa damu nyingi au shida kubwa ya kupumua.",
    },
    "HIV disease": {
        "name": "Ugonjwa wa VVU",
        "category": "Ugonjwa wa kuambukiza",
        "overview": (
            "VVU hushambulia kinga ya mwili. Bila matibabu kinaweza kuendelea kuwa UKIMWI. Kwa "
            "matibabu sahihi, watu wenye VVU huishi maisha marefu na yenye afya."
        ),
        "causes": [
            "Kujamiiana bila kinga na mtu anayeishi na VVU",
            "Kutoka kwa mama kwenda kwa mtoto wakati wa ujauzito, kujifungua au kunyonyesha",
            "Kuchangia sindano au kugusana na damu yenye maambukizi",
        ],
        "symptoms": [
            "Mara nyingi hakuna dalili kwa miaka mingi",
            "Mwanzoni: ugonjwa unaofanana na mafua wiki chache baada ya kuambukizwa",
            "Baadaye: kupungua uzito, maambukizi ya mara kwa mara, kuhara kwa muda mrefu, homa",
        ],
        "diagnosis": [
            "Vipimo vya haraka vya VVU, vinavyothibitishwa kwa utaratibu wa kitaifa",
            "Kipimo cha kiwango cha virusi (viral load) kufuatilia matibabu",
            "Kipimo cha CD4 katika hali fulani",
        ],
        "treatment": [
            "Dawa za kupunguza makali ya VVU (ARV) maisha yote, zianze mapema iwezekanavyo",
            "Mchanganyiko wenye dolutegravir hutumika sana kama matibabu ya kwanza",
            "Dawa za kinga dhidi ya magonjwa nyemelezi inapohitajika",
        ],
        "management": [
            "Meza ARV kila siku; kiwango cha virusi kisichoonekana humaanisha VVU haiambukizwi "
            "kwa kujamiiana (U=U)",
            "Vipimo vya kiwango cha virusi na kuhudhuria kliniki mara kwa mara",
            "Kinga: kondomu, PrEP, PEP ndani ya saa 72 baada ya hatari, kuzuia maambukizi kutoka "
            "kwa mama kwenda kwa mtoto, tohara ya hiari kwa wanaume",
        ],
        "urgent": "Hatari ya kuambukizwa (anza PEP ndani ya saa 72), au kuugua sana ukiwa kwenye matibabu.",
    },
    "Hypertension": {
        "name": "Shinikizo la juu la damu",
        "category": "Ugonjwa wa moyo na mishipa ya damu",
        "overview": (
            "Shinikizo la damu ambalo kila mara ni 140/90 mmHg au zaidi. Huitwa 'muuaji kimya' "
            "kwa sababu watu wengi hawana dalili."
        ),
        "causes": [
            "Mara nyingi hakuna chanzo kimoja (shinikizo la msingi)",
            "Vihatarishi: umri mkubwa, historia ya familia, chumvi nyingi, uzito mkubwa, kutofanya "
            "mazoezi, pombe, sigara, msongo wa mawazo",
            "Wakati mwingine husababishwa na ugonjwa wa figo au wa homoni",
        ],
        "symptoms": [
            "Mara nyingi hakuna",
            "Vipimo vya juu sana: maumivu makali ya kichwa, kuona ukungu, maumivu ya kifua, "
            "kupumua kwa shida, kuchanganyikiwa",
        ],
        "diagnosis": [
            "Shinikizo la damu kupimwa kwa usahihi angalau mara mbili tofauti",
            "Vipimo vya chanzo na madhara: figo, mkojo, sukari, kolesteroli, ECG",
        ],
        "treatment": [
            "Kubadilisha mtindo wa maisha kwa kila mtu",
            "Dawa kama calcium channel blockers, ACE inhibitors au ARBs, na thiazide diuretics, "
            "mara nyingi kwa mchanganyiko",
        ],
        "management": [
            "Meza dawa kila siku, hata ukijisikia vizuri",
            "Punguza chumvi, kula mboga na matunda zaidi, dumisha uzito mzuri",
            "Fanya mazoezi angalau dakika 150 kwa wiki",
            "Punguza pombe na acha kuvuta sigara",
            "Pima shinikizo la damu mara kwa mara",
        ],
        "urgent": "Maumivu ya kifua, udhaifu au ganzi ya ghafla, shida ya kuongea, au maumivu makali ya kichwa.",
    },
    "Diabetes mellitus (Type 2)": {
        "name": "Kisukari (aina ya 2)",
        "category": "Ugonjwa wa homoni na umetaboli",
        "overview": (
            "Hali ya muda mrefu ambapo mwili hautumii insulini vizuri, na kusababisha sukari ya juu "
            "kwenye damu. Aina ya 2 ndiyo inayowapata watu wazima zaidi."
        ),
        "causes": [
            "Mwili kutoitikia insulini na kupungua kwa uzalishaji wa insulini",
            "Vihatarishi: uzito mkubwa, kutofanya mazoezi, lishe isiyofaa, historia ya familia, "
            "umri mkubwa, kisukari wakati wa ujauzito",
        ],
        "symptoms": [
            "Kiu kingi na kukojoa mara kwa mara",
            "Uchovu na kuona ukungu",
            "Vidonda vinavyochelewa kupona na maambukizi ya mara kwa mara",
            "Watu wengi hawana dalili mwanzoni",
        ],
        "diagnosis": [
            "Sukari ya damu bila kula (fasting) ya 7.0 mmol/L au zaidi",
            "HbA1c ya 6.5% au zaidi",
            "Sukari ya wakati wowote ya 11.1 mmol/L au zaidi pamoja na dalili",
            "Kipimo cha uvumilivu wa sukari (OGTT)",
        ],
        "treatment": [
            "Lishe bora, mazoezi na kupunguza uzito",
            "Metformin mara nyingi ndiyo dawa ya kwanza",
            "Vidonge vingine au insulini inapohitajika",
        ],
        "management": [
            "Kupima sukari mara kwa mara",
            "Kuangalia miguu kila siku na macho kila mwaka",
            "Kudhibiti shinikizo la damu na kolesteroli",
            "Jua dalili za sukari kushuka: kutetemeka, kutokwa jasho, kuchanganyikiwa",
        ],
        "urgent": "Kuchanganyikiwa, kuzimia, sukari ya juu sana au chini sana, au kidonda cha mguu kinachozidi.",
    },
    "Pneumonia": {
        "name": "Nimonia",
        "category": "Ugonjwa wa mfumo wa kupumua",
        "overview": (
            "Maambukizi ya mapafu. Ni chanzo kikuu cha vifo vya watoto chini ya miaka 5, lakini mara "
            "nyingi inazuilika na inatibika."
        ),
        "causes": [
            "Bakteria (mf. Streptococcus pneumoniae), virusi au fangasi",
            "Hatari kubwa zaidi: watoto wadogo, wazee, utapiamlo, VVU, moshi wa kupikia ndani ya nyumba",
        ],
        "symptoms": [
            "Kikohozi na homa",
            "Kupumua haraka au kwa shida",
            "Maumivu ya kifua wakati wa kupumua",
            "Kwa watoto: sehemu ya chini ya kifua kuingia ndani wanapovuta pumzi",
        ],
        "diagnosis": [
            "Uchunguzi wa kitabibu, ikiwemo kuhesabu kasi ya kupumua",
            "Kiwango cha oksijeni mwilini (pulse oximeter)",
            "X-ray ya kifua inapopatikana",
        ],
        "treatment": [
            "Nimonia ya bakteria: antibiotiki kama amoxicillin",
            "Nimonia kali: huduma ya hospitali, oksijeni na antibiotiki za sindano",
        ],
        "management": [
            "Maliza dozi yote ya antibiotiki",
            "Chanjo: pneumococcal (PCV), Hib, surua na kifaduro",
            "Kunyonyesha maziwa ya mama pekee kwa miezi 6 ya kwanza na lishe bora",
            "Punguza moshi ndani ya nyumba na nawa mikono",
        ],
        "urgent": "Kushindwa kunywa, degedege, usingizi mzito sana, midomo ya bluu, au shida kubwa ya kupumua.",
    },
    "Asthma": {
        "name": "Pumu",
        "category": "Ugonjwa wa mfumo wa kupumua",
        "overview": (
            "Hali ya muda mrefu ambapo njia za hewa huvimba na kubana, na kufanya kupumua kuwa vigumu "
            "wakati wa shambulio."
        ),
        "causes": [
            "Kuvimba kwa njia za hewa, mara nyingi pamoja na mzio au historia ya familia",
            "Vichochezi vya kawaida: vumbi, moshi, chavua, hewa ya baridi, mazoezi, maambukizi ya kifua",
        ],
        "symptoms": [
            "Kupumua kwa mlio (wheezing) na kikohozi, mara nyingi zaidi usiku",
            "Kubanwa kifua",
            "Kupumua kwa shida",
        ],
        "diagnosis": [
            "Historia ya ugonjwa na uchunguzi wa kitabibu",
            "Kipimo cha mapafu (spirometry) kinachoonyesha njia za hewa kufunguka baada ya dawa",
            "Kufuatilia mtiririko wa hewa (peak flow)",
        ],
        "treatment": [
            "Pampu za haraka (reliever) kufungua njia za hewa wakati wa dalili",
            "Pampu za kinga (controller) zenye corticosteroid ya kuvuta kupunguza uvimbe",
            "Shambulio kali: huduma ya dharura, oksijeni na dawa nyingine",
        ],
        "management": [
            "Jifunze kutumia pampu kwa usahihi; spacer husaidia",
            "Fuata mpango wa maandishi wa kudhibiti pumu",
            "Epuka vichochezi unavyovijua na moshi",
            "Kuonana na mhudumu wa afya mara kwa mara",
        ],
        "urgent": "Kushindwa kuongea kwa kukosa pumzi, midomo ya bluu, au pampu ya haraka isiyosaidia.",
    },
    "Cholera": {
        "name": "Kipindupindu",
        "category": "Ugonjwa wa kuambukiza",
        "overview": (
            "Maambukizi ya kuhara ya ghafla yanayoweza kuua ndani ya saa chache yasipotibiwa, lakini "
            "hutibiwa kwa urahisi kwa kurudisha maji mwilini haraka."
        ),
        "causes": [
            "Bakteria Vibrio cholerae katika maji au chakula kichafu",
            "Usafi duni wa mazingira na maji yasiyo salama ya kunywa",
        ],
        "symptoms": [
            "Kuhara kwa ghafla, kwa wingi, kama maji ya mchele",
            "Kutapika",
            "Dalili za upungufu wa maji: kiu, macho kuingia ndani, kukojoa kidogo, udhaifu",
        ],
        "diagnosis": [
            "Utambuzi wa kitabibu wakati wa mlipuko",
            "Vipimo vya haraka na kuotesha kinyesi maabara kuthibitisha",
        ],
        "treatment": [
            "Maji ya ORS kwa wagonjwa wengi",
            "Upungufu mkubwa wa maji: maji ya mshipani (drip)",
            "Antibiotiki kwa wagonjwa mahututi; zinki kwa watoto",
        ],
        "management": [
            "Kunywa maji safi, yaliyochemshwa au kutibiwa",
            "Nawa mikono kwa sabuni baada ya choo na kabla ya kula",
            "Tumia choo; pika chakula vizuri na ukile kikiwa cha moto",
            "Chanjo ya kipindupindu ya kumeza katika maeneo hatari na wakati wa mlipuko",
        ],
        "urgent": "Kuhara maji mfululizo, kushindwa kunywa, au dalili za upungufu mkubwa wa maji.",
    },
}