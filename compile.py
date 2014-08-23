# coding=UTF-8
from __future__ import with_statement
import json, csv, sys
months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]

lang = "en"

i18n_data = {
    "en": {
        "high mercury": "high mercury",
        "not in season": "not in season",
        "In season in": "In season in",
        "january": "january",
        "february": "february",
        "march": "march",
        "april": "april",
        "may": "may",
        "june": "june",
        "july": "july",
        "august": "august",
        "september": "september",
        "october": "october",
        "november": "november",
        "december": "december"
    },
    "de": {
        "high mercury": "Quecksilber",
        "not in season": "nicht in Saison",
        "In season in": "Saison",
        "january": "Januar",
        "february": "Februar",
        "march": u'März',
        "april": "April",
        "may": "Mai",
        "june": "Juni",
        "july": "Juli",
        "august": "August",
        "september": "September",
        "october": "Oktober",
        "november": "November",
        "december": "Dezember"
    },
    "fr": {
        "high mercury": "Mercure",
        "not in season": "pas en saison",
        "In season in": "Saison",
        "january": "janvier",
        "february": u"f\xc3vrier",
        "march": 'mars',
        "april": "avril",
        "may": "mai",
        "june": "juin",
        "july": "juillet",
        "august": u"août",
        "september": "septembre",
        "october": "octobre",
        "november": "novembre",
        "december": u"décembre"
    }
}

if len(sys.argv) > 1:
    lang = sys.argv[1]
    
def _(text):
    return i18n_data[lang][text]

with open("fish.json") as f:
    data = json.loads(f.read())

with open("templates/page.html") as f:
    page_t = f.read()

with open("templates/monthsheet.html") as f:
    m_sheet_t = f.read()
    
with open("templates/yearsheet.html") as f:
    y_sheet_t = f.read()

with open("templates/entry.html") as f:
    entry_t = f.read()

with open("templates/source.html") as f:
    source_t = f.read()
    
with open("templates/detail.html") as f:
    detail_t = f.read()

data["categories"] = sorted([e for e in data["categories"] if "name_" + lang in e], key=lambda c: c["name_" + lang])

def sustainable(e, month):
    return e["sustainable"]
    #if month != "year" and "inSeason" in e:
    #    return "yes" if month in e["inSeason"] else "no"
    #else:
    #    return e["sustainable"]

def in_season_info(e, month):
    if month != "year" and "inSeason" in e:
        return "" if month in e["inSeason"] else "<br><span class=\"notinseason\">" + _("not in season") + "</span>"
    else:
        return ""

def mercury_info(e, c):
    if c and "mercury" in c and c["mercury"] == "high":
        return "<br><span class=\"mercury\">" + _("high mercury") + "</span>"
    if "mercury" in e and e["mercury"] == "high":
        return "<br><span class=\"mercury\">" + _("high mercury") + "</span>"
    return ""

def arrow(e, month):
    if sustainable(e, month) == "yes":
        #return "<span class=\"arrow-up\">&and; </span>"
        return "<img src=\"i/tick.png\" alt=\"yes\">"
    else:
        return "<img src=\"i/x.png\" alt=\"no\" style=\"padding-right: 2px\">"
        #return "<span class=\"arrow-down\">&or; </span>"
        
def versions():
    return " ".join([v[0] if v[0] == lang else "<a href=\"" + v[1] + "\">" + v[0] + "</a>" for v in data["versions"].iteritems()])

def entry(e, month):
    if e["sustainable"] == "depends":
        return "\n".join([entry_t.replace("{{sustainable}}", sustainable(c, month)).replace("{{name}}", arrow(c, month) + e["name_" + lang].strip() + " (" + c["name_" + lang] + ")").replace("{{link}}", "detail/" + (e["name_" + lang] + "_" + c["name_" + lang] + ".html").lower().replace(" ", "_").replace("/", "_")).replace("{{inSeason}}", in_season_info(c, month)).replace("{{mercury}}", mercury_info(e, c)) for c in e["categories"] if "name_" + lang in c])
    else:
        return entry_t.replace("{{sustainable}}", sustainable(e, month)).replace("{{name}}", arrow(e, month) + e["name_" + lang].strip()).replace("{{link}}", "detail/" + (e["name_" + lang] + ".html").lower().replace(" ", "_").replace("/", "_")).replace("{{inSeason}}", in_season_info(e, month)).replace("{{mercury}}", mercury_info(e, None))

def sheet(month_id):
    if month_id == "year":
        return y_sheet_t.replace("{{contents}}", "\n".join([entry(e, "year") for e in data["categories"] if "name_" + lang in e]))
    else:
        return m_sheet_t.replace("{{month}}", "(in " + months[month_id].capitalize() + ")").replace("{{name}}", "month-" + str(month_id)).replace("{{contents}}", "\n".join([entry(e, months[month_id]) for e in data["categories"] if "name_" + lang in e]))

def source(s):
    return source_t.replace("{{name}}", s[0]).replace("{{url}}", s[1])

main_page = page_t.replace("{{sources}}", "\n".join([source(s) for s in data["sources"]])).replace("{{contents}}", sheet("year") + "\n" + "\n".join([sheet(m) for m in range(0, 12)])).replace("{{explanation}}", data["explanation"]).replace("{{name}}", data["name_" + lang]).replace("{{slogan}}", data["slogan_" + lang]).replace("{{versions}}", versions()).replace("{{description}}", data["description_" + lang]).replace("{{keywords}}", data["keywords_" + lang])

with open(lang + "/index.html", 'w') as f:
    f.write(main_page.encode('utf-8'))

# Individual pages
def season_table(in_season):
    if in_season:
        return "<p>" + _("In season in") + ":<ul class=\"seasons\">"+ "\n".join(["<li>" + _(m).capitalize() + "</li>" for m in in_season])
    else:
        return ""
        
def detail_arrow(e, month):
    if sustainable(e, month) == "yes":
        return "<img src=\"../i/tick-large.png\" alt=\"yes\">"
    else:
        return "<img src=\"../i/x-large.png\" alt=\"no\">"

def output_detail(entry, file_name, name, desc, in_season, sources, explanation):
    print "detail/" + file_name + ".html"
    with open(lang + "/detail/" + file_name + ".html", 'w') as f:
        f.write(detail_t.replace("{{name}}", name).replace("{{sustainable}}", sustainable(entry, "year")).replace("{{arrow}}", detail_arrow(entry, "year")).replace("{{description}}", desc).replace("{{inSeason}}", season_table(in_season)).replace("{{explanation}}", explanation).replace("{{sources}}", "\n".join([source(s) for s in sources])).encode('utf-8'))

for e in [e for e in data["categories"] if "name_" + lang in e]:
    name = e["name_" + lang]
    file_name = name.lower().replace(" ", "_").replace("/", "_")
    desc = e["description"] + " " if "description" in e else ""
    in_season = e["inSeason"] if "inSeason" in e else None
    sources = e["sources"] if "sources" in e else []
    explanation = e["explanation"] + " " if "explanation" in e else ""
    if "categories" in e:
        for c in [c for c in e["categories"] if "name_" + lang in c]:
            c_name = name + " (" + c["name_" + lang] + ")"
            c_file_name = file_name + "_" + c["name_" + lang].lower().replace(" ", "_").replace("/", "_")
            c_desc = desc + (c["description"] if "description" in c else "")
            c_in_season = c["inSeason"] if "inSeason" in c else in_season
            c_sources = sources + (c["sources"] if "sources" in c else [])
            c_explanation = explanation + (c["explanation"] if "explanation" in c else "")
            output_detail(c, c_file_name, c_name, c_desc, c_in_season, c_sources, c_explanation)
    else:
        output_detail(e, file_name, name, desc, in_season, sources, explanation)

# Now convert the whole thing to CSV:
with open(lang + "/fish.csv", 'wb') as f:
    w = csv.writer(f)
    w.writerow(["Name", "Sustainable", "Mercury", "Description", "In Season", "Sources", "Explanation"])
    for e in [e for e in data["categories"] if "name_" + lang in e]:
        name = e["name_" + lang].strip()
        desc = e["description"] + " " if "description" in e else ""
        in_season = e["inSeason"] if "inSeason" in e else []
        sources = e["sources"] if "sources" in e else []
        explanation = e["explanation"] + " " if "explanation" in e else ""
        sustainable = e["sustainable"] == "yes"
        mercury = e["mercury"] if "mercury" in e else "?"
        if "categories" in e:
            for c in [c for c in e["categories"] if "name_" + lang in c]:
                c_name = name + " (" + c["name_" + lang] + ")"
                c_desc = desc + (c["description"] if "description" in c else "")
                c_in_season = c["inSeason"] if "inSeason" in c else in_season
                c_sources = sources + (c["sources"] if "sources" in c else [])
                c_explanation = explanation + (c["explanation"] if "explanation" in c else "")
                c_sustainable = c["sustainable"] == "yes"
                c_mercury = c["mercury"] if "mercury" in c else mercury
                w.writerow([c_name.encode('UTF-8'), c_sustainable, c_mercury, c_desc.encode('UTF-8'), ", ".join(c_in_season).encode('UTF-8'), ", ".join([s[1] for s in c_sources]).encode('UTF-8'), c_explanation.encode('UTF-8')])
        else:
            w.writerow([name.encode('UTF-8'), sustainable, mercury, desc.encode('UTF-8'), ", ".join(in_season).encode('UTF-8'), ", ".join([s[1] for s in sources]).encode('UTF-8'), explanation.encode('UTF-8')])