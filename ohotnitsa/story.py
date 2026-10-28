"""«ОХОТНИЦА» — мини-сериал для TikTok, 3 части по ~1 минуте.

Моя девушка охотится на гулей. Я — гуль.

Кадр: scene, p (параметры), lines [(кто, текст)], hold, amb, sfx [(имя, сек)], beat (играет бит).
Кто говорит:
  narr  — Марк за кадром (мысли)       mark — Марк вслух
  nika  — Ника, стажёр охотников       grach — командир Грач
  sova  — Сова, гуль-информатор        beast — дикий гуль
"""

SPEAKERS = {
    "narr":  {"name": "",       "color": "#ffffff"},
    "mark":  {"name": "МАРК",   "color": "#ff3b4a"},
    "nika":  {"name": "НИКА",   "color": "#8fd3ff"},
    "grach": {"name": "ГРАЧ",   "color": "#e6e6e6"},
    "sova":  {"name": "СОВА",   "color": "#ffc04a"},
    "beast": {"name": "???",    "color": "#ff6a2a"},
}

P1 = {
    "id": 1, "title": "Свидание",
    "shots": [
        {"scene": "hook", "p": {"lines": ["МОЯ ДЕВУШКА", "ОХОТИТСЯ НА ГУЛЕЙ"], "punch": "Я — ГУЛЬ"}, "beat": True, "pre": 0.2,
         "sfx": [("boom", 0.0), ("tentacle", 1.4)],
         "lines": [("narr", "Моя девушка охотится на гулей. А я — гуль.")]},
        {"scene": "cafe", "p": {}, "amb": "cafe", "beat": True,
         "lines": [("narr", "Её зовут Ника. Стажёр отряда «Белые перчатки». И сегодня у нас первое свидание.")]},
        {"scene": "face", "p": {"who": "nika", "bg": "cafe"}, "amb": "cafe",
         "lines": [("nika", "Говорят, у гулей глаза становятся чёрными. Я бы такого сразу узнала!")]},
        {"scene": "face", "p": {"who": "mark", "bg": "cafe", "lens": True}, "amb": "cafe",
         "lines": [("narr", "Я улыбнулся. И порадовался, что надел линзы.")]},
        {"scene": "window", "p": {}, "amb": "cafe", "sfx": [("crash", 0.2), ("siren", 0.5)],
         "lines": [("narr", "А потом с улицы донёсся крик.")]},
        {"scene": "face", "p": {"who": "nika", "bg": "cafe", "alarm": True}, "amb": "street", "sfx": [("whoosh", 1.6)],
         "lines": [("nika", "Сиди здесь! Это моя работа!")]},
        {"scene": "alley", "p": {}, "amb": "rain", "beat": True, "sfx": [("growl", 0.3), ("impact", 2.2), ("metal", 2.4)],
         "lines": [("beast", "Охотница... Маленькая. Сладкая."),
                   ("narr", "Она была стажёром. А это был взрослый гуль. Голодный.")]},
        {"scene": "eye", "p": {}, "amb": "drone", "sfx": [("heart", 0.3), ("heart", 1.3), ("heart", 2.3)],
         "lines": [("narr", "У меня было две секунды. Спрятаться... или показать, кто я.")]},
        {"scene": "reveal", "p": {"mask": True}, "beat": "drop", "pre": 0.3,
         "sfx": [("tentacle", 0.4), ("tentacle", 1.0), ("boom", 1.6)],
         "lines": [("narr", "Я выбрал второе.")], "hold": 1.6},
        {"scene": "smash", "p": {}, "beat": "drop", "pre": 0.1,
         "sfx": [("impact", 0.25), ("impact", 0.9), ("impact", 1.5), ("boom", 2.1)], "hold": 2.6},
        {"scene": "face", "p": {"who": "nika", "bg": "alley", "red": True}, "amb": "rain",
         "lines": [("nika", "Кто... ты такой?")]},
        {"scene": "leave", "p": {}, "amb": "rain", "sfx": [("glint", 2.6)],
         "lines": [("narr", "Я ушёл, не сказав ни слова. И не заметил, что от моей маски откололся кусок.")]},
        {"scene": "door", "p": {}, "amb": "room", "sfx": [("knock", 0.1), ("door", 0.9)], "pre": 1.4,
         "lines": [("nika", "Привет. Я нашла это на месте нападения."),
                   ("nika", "И знаешь что? Оно пахнет твоим одеколоном.")]},
        {"scene": "end", "p": {"next": 2, "name": "ПРОВЕРКА"}, "hold": 3.2, "sfx": [("boom", 0.1)]},
    ],
}

P2 = {
    "id": 2, "title": "Проверка",
    "shots": [
        {"scene": "hook", "p": {"lines": ["ОНА НАШЛА", "ОСКОЛОК МОЕЙ МАСКИ"], "punch": "ЧАСТЬ 2"}, "beat": True, "pre": 0.2,
         "sfx": [("boom", 0.0), ("glint", 1.0)],
         "lines": [("narr", "Она нашла осколок моей маски. И смотрела мне прямо в глаза.")]},
        {"scene": "face", "p": {"who": "mark", "bg": "room", "lens": True}, "amb": "room",
         "lines": [("narr", "Я соврал. Сказал, что был в том переулке и пытался помочь. Она поверила. Почти.")]},
        {"scene": "face", "p": {"who": "nika", "bg": "room"}, "amb": "room",
         "lines": [("nika", "Завтра отряд проверяет весь район. Новый сканер. Он находит гуля за одну секунду.")]},
        {"scene": "scanner", "p": {}, "amb": "drone", "sfx": [("scan", 0.3)],
         "lines": [("narr", "За одну секунду. А я живу в этом районе.")]},
        {"scene": "owl", "p": {}, "amb": "wind", "beat": True,
         "lines": [("sova", "Ох, Марк, Марк. Влюбиться в охотницу? Даже для гуля это слишком."),
                   ("sova", "Сканер чует клетки кагуне. Не ешь три дня — и они уснут.")]},
        {"scene": "hunger", "p": {}, "amb": "drone", "sfx": [("heart", 0.3), ("heart", 1.6), ("glitch", 3.0)],
         "lines": [("narr", "Три дня без еды. Для гуля это как три дня без воздуха.")]},
        {"scene": "checkpoint", "p": {"stage": "mark"}, "amb": "street", "beat": True, "sfx": [("scan", 1.2), ("ok", 2.6)],
         "lines": [("grach", "Следующий."),
                   ("narr", "Зелёный. Я прошёл.")]},
        {"scene": "checkpoint", "p": {"stage": "nika"}, "amb": "street", "sfx": [("scan", 0.6), ("alarm", 1.8)],
         "lines": [("narr", "А потом сканер поднесли к Нике. Просто для проверки.")]},
        {"scene": "face", "p": {"who": "grach", "bg": "street", "red": True}, "amb": "street", "sfx": [("sting", 0.2)],
         "lines": [("grach", "Стажёр Ника. Ты — гуль.")]},
        {"scene": "face", "p": {"who": "nika", "bg": "street", "red": True}, "amb": "street",
         "lines": [("nika", "Что?.. Нет. Это ошибка!")]},
        {"scene": "eye", "p": {"who": "nika"}, "amb": "drone", "sfx": [("heart", 0.2)],
         "lines": [("narr", "Она не врала. Она правда не знала, кто она.")]},
        {"scene": "end", "p": {"next": 3, "name": "ДВЕ МАСКИ"}, "hold": 3.2, "sfx": [("boom", 0.1)]},
    ],
}

P3 = {
    "id": 3, "title": "Две маски",
    "shots": [
        {"scene": "hook", "p": {"lines": ["ЕЁ ОБЪЯВИЛИ ГУЛЕМ.", "ЕЁ ЖЕ ОТРЯД"], "punch": "ФИНАЛ"}, "beat": True, "pre": 0.2,
         "sfx": [("boom", 0.0), ("siren", 0.8)],
         "lines": [("narr", "Её объявили гулем. Её же отряд. И приказ был только один.")]},
        {"scene": "face", "p": {"who": "grach", "bg": "roof"}, "amb": "wind", "sfx": [("reload", 1.8)],
         "lines": [("grach", "Без суда. Она опасна. Огонь по моей команде.")]},
        {"scene": "roof", "p": {"stage": "corner"}, "amb": "wind", "beat": True,
         "lines": [("narr", "У неё не было кагуне. Не было маски. Был только я.")]},
        {"scene": "reveal", "p": {"mask": False, "land": True}, "beat": "drop", "pre": 0.2,
         "sfx": [("boom", 0.2), ("tentacle", 0.7)],
         "lines": [("mark", "Хотите её? Сначала меня.")]},
        {"scene": "face", "p": {"who": "nika", "bg": "roof"}, "amb": "wind",
         "lines": [("nika", "Марк?.. Твои глаза..."),
                   ("mark", "Прости. Линзы.")]},
        {"scene": "duel", "p": {}, "beat": "drop", "pre": 0.2,
         "sfx": [("blade", 0.3), ("impact", 0.9), ("blade", 1.7), ("impact", 2.4), ("blade", 3.2)],
         "lines": [("grach", "Гуль защищает гуля. Как трогательно.")]},
        {"scene": "face", "p": {"who": "mark", "bg": "roof", "hurt": True}, "amb": "wind", "sfx": [("impact", 0.1), ("heart", 0.9)],
         "lines": [("narr", "Его клинок вошёл мне в плечо. И я понял, что не успею.")]},
        {"scene": "wings", "p": {}, "beat": "drop", "pre": 0.4, "sfx": [("crystal", 0.3), ("boom", 1.2), ("crystal", 2.0)],
         "lines": [("narr", "А потом за её спиной раскрылись крылья.")], "hold": 1.5},
        {"scene": "smash", "p": {"wings": True}, "beat": "drop", "pre": 0.1,
         "sfx": [("crystal", 0.2), ("impact", 0.6), ("impact", 1.2), ("boom", 1.8)], "hold": 2.4},
        {"scene": "dawn", "p": {}, "amb": "wind",
         "lines": [("nika", "Значит, на первом свидании ты мне врал."),
                   ("mark", "Ну... ты тоже. Просто сама не знала.")]},
        {"scene": "dawn", "p": {"close": True}, "amb": "wind", "beat": True,
         "lines": [("narr", "Теперь на нас охотится весь город. Но впервые в жизни... я не один.")]},
        {"scene": "end", "p": {"next": 0, "name": "СЕЗОН 2?"}, "hold": 3.5, "sfx": [("boom", 0.1)]},
    ],
}

PARTS = [P1, P2, P3]
