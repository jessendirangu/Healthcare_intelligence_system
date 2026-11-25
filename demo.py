"""Narrated demonstrations in English and Kiswahili.

Each demo is a short series of animated scenes (drawn with SVG, so they
load instantly and use almost no data). When the user taps Play, the
phone's built-in voice reads each step aloud in the chosen language, with
captions on screen. If the device has no voice for that language, the
captions still play step by step.

Use:   demo.show("waist")          a narrated demonstration
       demo.breathing_practice()   practise counting a child's breathing
"""

import json

import streamlit.components.v1 as components

import i18n

ACCENT = "#2F7D6D"
RED = "#C0392B"


# ---------------------------------------------------------------
# Simple drawings (SVG). Each returns the inside of a 320x220 picture.
# ---------------------------------------------------------------

def _person(extra="", arms="down"):
    arm = {"down": '<path d="M160 92 L128 140 M160 92 L192 140" />',
           "up": '<path d="M160 92 L112 70 M160 92 L208 70" />'}.get(arms, "")
    return f"""
    <g stroke="#3B4A47" stroke-width="7" stroke-linecap="round" fill="none">
      <circle cx="160" cy="48" r="22" fill="#F2D2B6" stroke="#3B4A47" stroke-width="4"/>
      <path d="M160 72 L160 150" />{arm}
      <path d="M160 150 L138 205 M160 150 L182 205" />
    </g>{extra}"""


def _icon(symbol, color=ACCENT):
    return f"""<circle cx="160" cy="105" r="70" fill="{color}22"/>
    <text x="160" y="132" font-size="78" text-anchor="middle">{symbol}</text>"""


def _face(droop=False):
    mouth = ("M135 140 Q160 160 185 140" if not droop else "M135 132 Q160 152 185 148")
    eye = '<circle cx="182" cy="96" r="6"/>' if not droop else '<ellipse cx="182" cy="100" rx="7" ry="4"/>'
    anim = ('<animate attributeName="d" dur="1.6s" repeatCount="indefinite" '
            'values="M135 140 Q160 160 185 140;M135 132 Q160 152 185 150;M135 132 Q160 152 185 150"/>'
            if droop else "")
    return f"""<circle cx="160" cy="110" r="70" fill="#F2D2B6" stroke="#3B4A47" stroke-width="4"/>
    <g fill="#3B4A47"><circle cx="138" cy="96" r="6"/>{eye}</g>
    <path d="{mouth}" stroke="#3B4A47" stroke-width="6" fill="none" stroke-linecap="round">{anim}</path>"""


def _string_waist():
    return _person("""
    <ellipse cx="160" cy="118" rx="34" ry="9" fill="none" stroke="#C27C2C" stroke-width="5"
             stroke-dasharray="220" stroke-dashoffset="220">
      <animate attributeName="stroke-dashoffset" from="220" to="0" dur="2s" fill="freeze"/>
    </ellipse>
    <circle cx="160" cy="118" r="4" fill="#3B4A47"/>""")


def _ruler():
    ticks = "".join(f'<line x1="{40 + i * 24}" y1="120" x2="{40 + i * 24}" '
                    f'y2="{105 if i % 5 else 98}" stroke="#3B4A47" stroke-width="2"/>'
                    for i in range(11))
    return f"""<rect x="30" y="98" width="260" height="40" rx="4" fill="#F4E3B5" stroke="#3B4A47" stroke-width="2"/>
    {ticks}
    <line x1="30" y1="160" x2="30" y2="160" stroke="#C27C2C" stroke-width="5">
      <animate attributeName="x2" from="30" to="290" dur="2s" fill="freeze"/></line>"""


def _sitting():
    return """<g stroke="#3B4A47" stroke-width="7" stroke-linecap="round" fill="none">
      <circle cx="120" cy="45" r="20" fill="#F2D2B6" stroke-width="4"/>
      <path d="M120 66 L120 130 L170 130 L170 195" /><path d="M120 85 L175 110 L235 110"/>
      <path d="M95 60 L95 140" stroke="#9BA8A5"/></g>
    <rect x="205" y="112" width="90" height="8" fill="#9BA8A5"/>
    <rect x="150" y="96" width="34" height="22" rx="5" fill="#6B8FA3">
      <animate attributeName="opacity" values="1;0.5;1" dur="1.5s" repeatCount="indefinite"/></rect>
    <path d="M150 195 L195 195" stroke="#3B4A47" stroke-width="7" stroke-linecap="round"/>"""


def _arm_drift():
    return _person("""
    <path d="M160 92 L112 70" stroke="#3B4A47" stroke-width="7" stroke-linecap="round"/>
    <path d="M160 92 L208 70" stroke="#C0392B" stroke-width="7" stroke-linecap="round">
      <animate attributeName="d" dur="2.5s" fill="freeze" values="M160 92 L208 70;M160 92 L200 118"/>
    </path>""", arms=None)


def _baby(rate=None):
    """A baby lying down; the chest rises and falls at `rate` breaths per minute."""
    period = 60 / rate if rate else 1.4
    return f"""<rect x="40" y="150" width="240" height="14" rx="7" fill="#E9EFED"/>
    <circle cx="80" cy="118" r="26" fill="#F2D2B6" stroke="#3B4A47" stroke-width="3"/>
    <ellipse cx="170" cy="128" rx="70" ry="24" fill="#BFD8D1" stroke="#3B4A47" stroke-width="3">
      <animate attributeName="ry" values="22;32;22" dur="{period:.3f}s" repeatCount="indefinite"/>
      <animate attributeName="cy" values="130;122;130" dur="{period:.3f}s" repeatCount="indefinite"/>
    </ellipse>"""


def _clock():
    return f"""<circle cx="160" cy="110" r="70" fill="#fff" stroke="#3B4A47" stroke-width="5"/>
    <line x1="160" y1="110" x2="160" y2="55" stroke="{ACCENT}" stroke-width="6" stroke-linecap="round">
      <animateTransform attributeName="transform" type="rotate" from="0 160 110" to="360 160 110"
                        dur="4s" repeatCount="indefinite"/></line>
    <circle cx="160" cy="110" r="6" fill="#3B4A47"/>"""


# ---------------------------------------------------------------
# The demonstrations: (scene, English text, Kiswahili text)
# ---------------------------------------------------------------

DEMOS = {
    "waist": {
        "title": ("How to measure your waist with a string", "Jinsi ya kupima kiuno kwa kamba"),
        "steps": [
            (_person(), "Stand up straight and breathe out normally.",
             "Simama wima na upumue kawaida."),
            (_string_waist(), "Put a string around your waist, at the level of your belly button. "
             "Keep it straight, not tight.",
             "Zungusha kamba kiunoni, usawa wa kitovu. Iwe sawa, isibane."),
            (_icon("✋"), "Hold the place where the two ends of the string meet.",
             "Shika mahali ncha mbili za kamba zinapokutana."),
            (_ruler(), "Lay the string flat and measure it with a ruler or tape. A school ruler is "
             "30 centimetres long.",
             "Laza kamba chini na uipime kwa rula au tepu. Rula ya shule ina urefu wa sentimita 30."),
            (_icon("📏"), "For women, a waist above 80 centimetres raises the risk of diabetes. "
             "For men, above 94 centimetres.",
             "Kwa wanawake, kiuno zaidi ya sentimita 80 huongeza hatari ya kisukari. "
             "Kwa wanaume, zaidi ya sentimita 94."),
        ],
    },
    "bp": {
        "title": ("How to measure blood pressure correctly", "Jinsi ya kupima shinikizo la damu kwa usahihi"),
        "steps": [
            (_icon("🚭"), "For 30 minutes before, don't smoke, drink coffee or tea, or exercise.",
             "Kwa dakika 30 kabla, usivute sigara, usinywe kahawa au chai, wala usifanye mazoezi."),
            (_clock(), "Empty your bladder, then sit quietly for 5 minutes with your back supported.",
             "Kojoa kwanza, kisha kaa kimya kwa dakika 5 mgongo ukiwa umeegemea."),
            (_sitting(), "Keep both feet flat on the floor and don't cross your legs. Rest your arm on a "
             "table so the cuff is at the level of your heart.",
             "Weka nyayo zote mbili sakafuni na usikunje miguu. Weka mkono mezani ili kifaa kiwe "
             "usawa wa moyo."),
            (_icon("🤫"), "Put the cuff on bare skin, not over clothes. Don't talk while it measures.",
             "Funga kifaa kwenye ngozi, si juu ya nguo. Usiongee wakati kinapima."),
            (_icon("✍️"), "Take two readings, one minute apart, and write down both.",
             "Pima mara mbili, dakika moja kati yake, na uandike vipimo vyote viwili."),
        ],
    },
    "fast": {
        "title": ("Stroke: think FAST", "Kiharusi: kumbuka FAST"),
        "steps": [
            (_face(), "A stroke can be recognised in seconds. Think FAST.",
             "Kiharusi kinaweza kutambuliwa kwa sekunde chache. Kumbuka FAST."),
            (_face(droop=True), "F is for Face. Ask the person to smile. Does one side of the face droop?",
             "F ni Uso. Mwambie mtu atabasamu. Je, upande mmoja wa uso umelegea?"),
            (_arm_drift(), "A is for Arms. Ask them to lift both arms. Does one arm drift down?",
             "A ni Mikono. Mwambie anyanyue mikono yote miwili. Je, mkono mmoja unashuka?"),
            (_icon("💬"), "S is for Speech. Is their speech slurred or strange? Can they repeat a simple sentence?",
             "S ni Usemi. Je, anaongea kwa shida au kwa namna ya ajabu? Anaweza kurudia sentensi rahisi?"),
            (_icon("🚑", RED), "T is for Time. Go to hospital immediately. Call 999 or 112 and note the time the "
             "signs started.",
             "T ni Muda. Nenda hospitali mara moja. Piga 999 au 112 na uandike saa dalili zilipoanza."),
        ],
    },
    "child_breathing": {
        "title": ("How to count a child's breathing", "Jinsi ya kuhesabu pumzi za mtoto"),
        "steps": [
            (_baby(), "Wait until the child is calm, not crying or feeding.",
             "Subiri mtoto atulie, asiwe analia wala ananyonya."),
            (_baby(), "Lift the child's clothes so you can see the chest or belly move.",
             "Inua nguo za mtoto ili uone kifua au tumbo likipanda na kushuka."),
            (_clock(), "Count each time the chest rises, for one full minute. Use a watch, phone or "
             "the practice timer below.",
             "Hesabu kila kifua kinapopanda, kwa dakika moja kamili. Tumia saa, simu au kipima muda "
             "cha mazoezi hapa chini."),
            (_icon("⚠️", RED), "Breathing is fast if it is 50 or more for a child aged 2 to 12 months, or 40 "
             "or more for a child aged 1 to 5 years. Fast breathing can mean pneumonia. Go to a "
             "clinic today.",
             "Kupumua ni haraka kama ni 50 au zaidi kwa mtoto wa miezi 2 hadi 12, au 40 au zaidi kwa "
             "mtoto wa mwaka 1 hadi miaka 5. Kupumua haraka kunaweza kumaanisha nimonia. Nenda kliniki leo."),
        ],
    },
    "child_danger": {
        "title": ("Danger signs in a sick child", "Dalili za hatari kwa mtoto mgonjwa"),
        "steps": [
            (_icon("🍼", RED), "The child cannot drink or breastfeed.", "Mtoto hawezi kunywa wala kunyonya."),
            (_icon("🤮", RED), "The child vomits everything.", "Mtoto anatapika kila kitu."),
            (_icon("⚡", RED), "The child has had convulsions, or fits.", "Mtoto amepata degedege."),
            (_icon("😴", RED), "The child is very sleepy or hard to wake.",
             "Mtoto ana usingizi mzito sana au ni vigumu kumwamsha."),
            (_icon("🏥", RED), "Any one of these signs is an emergency. Take the child to hospital now.",
             "Dalili yoyote kati ya hizi ni dharura. Mpeleke mtoto hospitali sasa."),
        ],
    },
    "pregnancy_danger": {
        "title": ("Danger signs in pregnancy", "Dalili za hatari wakati wa ujauzito"),
        "steps": [
            (_icon("🩸", RED), "Bleeding from the vagina.", "Kutokwa na damu ukeni."),
            (_icon("🤕", RED), "Severe headache with blurred vision, or fits.",
             "Maumivu makali ya kichwa na kuona ukungu, au degedege."),
            (_icon("🤰", RED), "The baby moves less than usual, or the waters break before labour.",
             "Mtoto tumboni anacheza kidogo kuliko kawaida, au maji yanatoka kabla ya uchungu."),
            (_icon("🌡️", RED), "Fever, severe belly pain, swelling of the face or hands, or difficult breathing.",
             "Homa, maumivu makali ya tumbo, kuvimba uso au mikono, au shida ya kupumua."),
            (_icon("🏥", RED), "Any one of these signs: go to a health facility immediately. Take your "
             "Mother and Child Health booklet.",
             "Dalili yoyote kati ya hizi: nenda kituo cha afya mara moja. Beba kitabu chako cha Afya "
             "ya Mama na Mtoto."),
        ],
    },
    "newborn_danger": {
        "title": ("Danger signs in a baby under 2 months", "Dalili za hatari kwa mtoto chini ya miezi 2"),
        "steps": [
            (_icon("🍼", RED), "The baby is not feeding well.", "Mtoto hanyonyi vizuri."),
            (_baby(70), "The baby breathes fast, 60 or more times a minute, or the chest sucks in.",
             "Mtoto anapumua haraka, mara 60 au zaidi kwa dakika, au kifua kinaingia ndani."),
            (_icon("🌡️", RED), "The baby feels hot, or feels cold.", "Mwili wa mtoto ni wa moto, au ni wa baridi."),
            (_icon("😶", RED), "The baby moves only when touched, has fits, or has yellow palms and soles.",
             "Mtoto anajitikisa tu akiguswa, ana degedege, au viganja na nyayo ni za njano."),
            (_icon("🏥", RED), "Babies get very sick very fast. Any sign: go to hospital now, keeping the "
             "baby warm, skin to skin.",
             "Watoto wachanga huugua sana kwa haraka. Dalili yoyote: nenda hospitali sasa, ukimweka "
             "mtoto kwenye joto, ngozi kwa ngozi."),
        ],
    },
}

UI = {
    "play": ("▶ Play", "▶ Cheza"),
    "pause": ("⏸ Pause", "⏸ Simamisha"),
    "replay": ("↺ Replay", "↺ Rudia"),
    "step": ("Step", "Hatua"),
    "no_voice": ("Your phone has no voice for this language, so read the captions. "
                 "To add one: phone Settings, then Text-to-speech, then install the language.",
                 "Simu yako haina sauti ya lugha hii, kwa hiyo soma maandishi. Kuongeza sauti: "
                 "Mipangilio ya simu, kisha Text-to-speech, kisha sakinisha lugha ya Kiswahili."),
}


def _pick(pair):
    return pair[1] if i18n.lang() == "sw" else pair[0]


def show(name, height=440):
    """Show a narrated demonstration in the user's chosen language."""
    demo = DEMOS[name]
    steps = [{"svg": svg, "text": _pick((en, sw))} for svg, en, sw in demo["steps"]]
    data = {
        "title": _pick(demo["title"]),
        "steps": steps,
        "lang": "sw" if i18n.lang() == "sw" else "en",
        "ui": {k: _pick(v) for k, v in UI.items()},
    }
    components.html(_PLAYER.replace("__DATA__", json.dumps(data)), height=height)


_PLAYER = """
<div id="demo" style="font-family:sans-serif;border:1px solid #DCE5E2;border-radius:14px;
     background:#fff;padding:14px;max-width:560px;margin:auto;">
  <div id="title" style="font-weight:700;color:#2F7D6D;margin-bottom:6px"></div>
  <svg id="scene" viewBox="0 0 320 220" style="width:100%;height:220px;background:#F5F9F8;border-radius:10px"></svg>
  <div id="caption" style="min-height:66px;font-size:17px;line-height:1.45;color:#1F2D2B;margin:10px 2px"></div>
  <div style="display:flex;gap:8px;align-items:center">
    <button id="play" style="background:#2F7D6D;color:#fff;border:0;border-radius:8px;padding:10px 16px;font-size:15px"></button>
    <button id="replay" style="background:#E9EFED;color:#1F2D2B;border:0;border-radius:8px;padding:10px 14px;font-size:15px"></button>
    <span id="count" style="margin-left:auto;color:#5B6B67;font-size:13px"></span>
  </div>
  <div id="dots" style="display:flex;gap:6px;margin-top:10px"></div>
  <div id="novoice" style="display:none;font-size:12.5px;color:#8A5A00;background:#FFF6E0;
       border-radius:8px;padding:8px;margin-top:10px"></div>
</div>
<script>
const D = __DATA__;
const synth = window.speechSynthesis;
let i = 0, playing = false, timer = null;
const $ = id => document.getElementById(id);
$("title").textContent = D.title;
$("replay").textContent = D.ui.replay;
$("novoice").textContent = D.ui.no_voice;

function findVoice() {
  if (!synth) return null;
  const voices = synth.getVoices();
  return voices.find(v => v.lang.toLowerCase().startsWith(D.lang + "-ke"))
      || voices.find(v => v.lang.toLowerCase().startsWith(D.lang)) || null;
}
function dots() {
  $("dots").innerHTML = D.steps.map((_, k) =>
    `<span style="flex:1;height:5px;border-radius:3px;background:${k <= i ? '#2F7D6D' : '#DCE5E2'}"></span>`).join("");
}
function render() {
  $("scene").innerHTML = D.steps[i].svg;
  $("caption").textContent = D.steps[i].text;
  $("count").textContent = `${D.ui.step} ${i + 1} / ${D.steps.length}`;
  $("play").textContent = playing ? D.ui.pause : D.ui.play;
  dots();
}
function next() {
  if (!playing) return;
  if (i < D.steps.length - 1) { i++; render(); speak(); }
  else { playing = false; render(); }
}
function speak() {
  clearTimeout(timer);
  const text = D.steps[i].text;
  const voice = findVoice();
  if (synth && voice) {
    synth.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.voice = voice; u.lang = voice.lang; u.rate = 0.92;
    u.onend = () => { timer = setTimeout(next, 700); };
    synth.speak(u);
  } else {
    $("novoice").style.display = "block";
    timer = setTimeout(next, Math.max(3500, text.length * 75));  // reading time
  }
}
$("play").onclick = () => {
  playing = !playing;
  if (playing) { if (i === D.steps.length - 1) i = 0; render(); speak(); }
  else { clearTimeout(timer); if (synth) synth.cancel(); render(); }
};
$("replay").onclick = () => { i = 0; playing = true; render(); speak(); };
if (synth) synth.onvoiceschanged = () => {};
render();
</script>
"""


# ---------------------------------------------------------------
# Practice: count an animated baby's breathing for 60 seconds
# ---------------------------------------------------------------

_PRACTICE_UI = {
    "title": ("Practice: count the baby's breathing", "Mazoezi: hesabu pumzi za mtoto"),
    "intro": ("Tap Start, count each time the chest rises for 60 seconds, then type your count.",
              "Bonyeza Anza, hesabu kila kifua kinapopanda kwa sekunde 60, kisha andika hesabu yako."),
    "start": ("Start 60 seconds", "Anza sekunde 60"),
    "your": ("Your count", "Hesabu yako"),
    "check": ("Check", "Angalia"),
    "again": ("Try another baby", "Jaribu mtoto mwingine"),
    "right": ("Well done! The baby breathed {r} times a minute. You counted {c}.",
              "Hongera! Mtoto alipumua mara {r} kwa dakika. Wewe ulihesabu {c}."),
    "close": ("Close! The baby breathed {r} times a minute. You counted {c}. Try again and count slowly.",
              "Karibu! Mtoto alipumua mara {r} kwa dakika. Wewe ulihesabu {c}. Jaribu tena, hesabu polepole."),
    "fast": ("For a child of 1 to 5 years this IS fast breathing (40 or more).",
             "Kwa mtoto wa mwaka 1 hadi miaka 5, huku NI kupumua haraka (40 au zaidi)."),
    "normal": ("For a child of 1 to 5 years this is NOT fast breathing (below 40).",
               "Kwa mtoto wa mwaka 1 hadi miaka 5, huku SI kupumua haraka (chini ya 40)."),
    "go": ("Count now...", "Hesabu sasa..."),
    "done": ("Time's up! Type how many breaths you counted.", "Muda umekwisha! Andika pumzi ulizohesabu."),
}


def breathing_practice():
    ui = {k: _pick(v) for k, v in _PRACTICE_UI.items()}
    html = _PRACTICE.replace("__UI__", json.dumps(ui)).replace("__BABY__", json.dumps(_baby(1)))
    components.html(html, height=470)


_PRACTICE = """
<div style="font-family:sans-serif;border:1px solid #DCE5E2;border-radius:14px;background:#fff;
     padding:14px;max-width:560px;margin:auto;">
  <div id="t" style="font-weight:700;color:#2F7D6D"></div>
  <div id="intro" style="font-size:14px;color:#5B6B67;margin:4px 0 8px"></div>
  <svg id="scene" viewBox="0 0 320 220" style="width:100%;height:200px;background:#F5F9F8;border-radius:10px"></svg>
  <div id="clock" style="font-size:30px;font-weight:800;text-align:center;color:#1F2D2B;margin:6px 0">60</div>
  <div id="msg" style="text-align:center;color:#5B6B67;min-height:20px"></div>
  <div style="display:flex;gap:8px;margin-top:8px">
    <button id="start" style="flex:1;background:#2F7D6D;color:#fff;border:0;border-radius:8px;padding:11px;font-size:15px"></button>
  </div>
  <div style="display:flex;gap:8px;margin-top:8px">
    <input id="count" type="number" inputmode="numeric" style="flex:1;padding:10px;font-size:16px;border:1px solid #C9D6D2;border-radius:8px">
    <button id="check" style="background:#E9EFED;border:0;border-radius:8px;padding:10px 16px;font-size:15px"></button>
  </div>
  <div id="result" style="margin-top:10px;font-size:15px;line-height:1.45"></div>
</div>
<script>
const U = __UI__;
const $ = id => document.getElementById(id);
let rate, left = 60, tick = null;
$("t").textContent = U.title; $("intro").textContent = U.intro;
$("start").textContent = U.start; $("check").textContent = U.check;
$("count").placeholder = U.your;
function newBaby() {
  rate = 28 + Math.floor(Math.random() * 30);     // 28-57 breaths a minute
  const period = (60 / rate).toFixed(3);
  $("scene").innerHTML = __BABY__.replace(/dur="[0-9.]+s"/g, `dur="${period}s"`);
  left = 60; $("clock").textContent = left; $("msg").textContent = "";
  $("result").textContent = ""; $("count").value = "";
}
$("start").onclick = () => {
  if ($("start").textContent === U.again) { newBaby(); $("start").textContent = U.start; return; }
  clearInterval(tick); left = 60; $("msg").textContent = U.go;
  tick = setInterval(() => {
    left--; $("clock").textContent = left;
    if (left <= 0) { clearInterval(tick); $("msg").textContent = U.done; }
  }, 1000);
};
$("check").onclick = () => {
  const c = parseInt($("count").value);
  if (isNaN(c)) return;
  const good = Math.abs(c - rate) <= 3;
  const fmt = s => s.replace("{r}", rate).replace("{c}", c);
  $("result").innerHTML = `<div style="padding:10px;border-radius:8px;background:${good ? '#E6F4EA' : '#FFF6E0'}">`
    + fmt(good ? U.right : U.close) + "<br><b>" + (rate >= 40 ? U.fast : U.normal) + "</b></div>";
  $("start").textContent = U.again;
};
newBaby();
</script>
"""


UI_WATCH = ("▶ Watch the demonstration", "▶ Tazama maonyesho")


def watch_label():
    return _pick(UI_WATCH)