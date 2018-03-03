var imgPreview, imgC, imgCTX,
    badgeCols = [["basic", 500, [220, 220, 220], 0], ["bronze", 3500, [236, 200, 172], 500], ["silver", 26E3, [185, 213, 223], 4E3], ["gold", 0, [255, 212, 88], 3E4]],
    badgePos = 0, bYoff = 100, fuzzyMode = !1, fuzz = 4, minCore = 3, pageContent, results, gymSelectHost, graphHost,
    appraisalMode = !1, imageScaleVal = 1, tmpXoffset = 0, percentages, yList = [], barList = [],
    sliceList = {hori: [], vert: []}, previouslySelected = !1, darkMode = !1,
    hasLocalStorage = "localStorage" in window && localStorage, language = "en", polyglot;
onload = function () {
    if (hasLocalStorage && localStorage.getItem("gymConfig")) {
        var a = JSON.parse(localStorage.getItem("gymConfig"));
        a.darkMode && (darkMode = a.darkMode);
        if (a.language) var b = a.language
    }
    darkMode && updateBodyClasses();
    document.getElementById("toggleDarkMode").addEventListener("click", toggleDarkMode);
    pageContent = document.getElementById("pageContent");
    results = document.getElementById("results");
    percentages = document.getElementById("percentages");
    imgPreview = document.getElementById("imgPreview");
    gymSelectHost =
        document.getElementById("gymSelectHost");
    graphHost = document.getElementById("graphHost");
    imgC = document.createElement("canvas");
    imgCTX = imgC.getContext("2d", {alpha: !1});
    document.getElementById("modeBadge").addEventListener("click", changeMode);
    document.getElementById("modeList").addEventListener("click", changeMode);
    document.addEventListener("click", toggleMenu);
    b && langStrs[b] ? language = b : (a = window.navigator.languages || [window.navigator.language || window.navigator.userLanguage], language = langStrs[a[0]] ? a[0] :
        a[0].substr(0, 2).toLowerCase());
    language && langStrs && Polyglot ? changeLanguage() : console.error("Unable to continue: Language support is missing");
    a = document.getElementById("page");
    a.addEventListener("dragenter", noEvent);
    a.addEventListener("dragover", noEvent);
    a.addEventListener("drop", handleDrop);
    loctionhostname = window[s[2]][s[0]];
    hostTest = -1 < loctionhostname.indexOf(s[1]);
    document.getElementById("modeSelect")
};

function handleDrop(a) {
    noEvent(a);
    a = a.dataTransfer.files[0];
    document.body == document.getElementById("page").parentNode && a && a.type && ("image/" == a.type.substr(0, 6) || "application/image" == a.type) && loadNewImage(a)
}

function noEvent(a) {
    a.stopPropagation();
    a.preventDefault()
}

function changeLanguage() {
    langStrs[language] || (language = "en");
    if ("strings.js" != document.scripts[0].src || "polyglot.js/index.js" != document.scripts[1].src) fuzz = 0;
    polyglot ? (polyglot.extend(langStrs[language]), polyglot.locale(language)) : polyglot = new Polyglot({
        locale: language,
        phrases: langStrs[language]
    });
    document.getElementById("title").textContent = polyglot.t("title");
    document.getElementById("imgPickerLabel").textContent = polyglot.t("appraiseButton");
    document.getElementById("toggleDarkMode").childNodes[0].textContent =
        polyglot.t("darkMode");
    document.getElementById("pickLanguage").childNodes[0].textContent = polyglot.t("languages");
    document.getElementById("showTrackedPage").childNodes[0].textContent = polyglot.t("trackedGyms");
    document.getElementById("trackedCont").children[0].textContent = polyglot.t("selectTrackedTitle");
    document.getElementById("trackedClose").textContent = polyglot.t("close");
    document.getElementById("gymBackupHost").children[1].childNodes[1].textContent = polyglot.t("backup");
    document.getElementById("gymBackupHost").children[3].childNodes[1].textContent =
        polyglot.t("restore");
    document.getElementById("langSelectTitle").textContent = polyglot.t("languages");
    document.getElementById("langClose").textContent = polyglot.t("close");
    document.getElementsByTagName("footer")[0].childNodes[0].textContent = polyglot.t("madeByQOAL");
    document.getElementById("miniMenu").childNodes[0].childNodes[1].childNodes[0].textContent = polyglot.t("madeByQOAL");
    document.getElementById("miniMenu").childNodes[0].childNodes[3].childNodes[0].textContent = polyglot.t("paypalText")
}

function toggleDarkMode() {
    darkMode = !darkMode;
    updateBodyClasses();
    hasLocalStorage && localStorage.setItem("gymConfig", JSON.stringify({darkMode: darkMode, language: language}));
    showMiniMenu(!0)
}

function updateBodyClasses() {
    document.body.setAttribute("class", (appraisalMode ? "list" : "") + (darkMode ? " dark" : ""))
}

function changeMode(a) {
    var b = appraisalMode;
    appraisalMode = "modeBadge" !== a.target.id;
    document.getElementById("modeBadge").setAttribute("class", appraisalMode ? "circle" : "circle selected");
    document.getElementById("modeList").setAttribute("class", appraisalMode ? "circle selected" : "circle");
    updateBodyClasses();
    if (b != appraisalMode && imgPreview.hasAttribute("data-show")) {
        imgPreview.src = "";
        imgPreview.removeAttribute("data-show");
        for (setResult(); percentages.firstChild;) percentages.removeChild(percentages.firstChild);
        pageContent.setAttribute("class", "")
    }
    gymSelectHost.hasAttribute("data-show") && gymSelectHost.removeAttribute("data-show");
    hideGraph();
    playTouchCircles(a.target.offsetLeft - 93 + "px", !1)
}

function playTouchCircles(a, b) {
    var c = document.getElementById("touchCircles");
    c.removeAttribute("class");
    c.offsetLeft;
    c.style.left = b ? "" : a;
    c.style.right = a ? "" : b;
    c.setAttribute("class", "animate");
    c.childNodes[1].addEventListener("animationend", endTouchCircles, !1)
}

function endTouchCircles(a) {
    document.getElementById("touchCircles").removeAttribute("class")
}

for (var s = [[15, 21, 24, 24, 17, 3, 14, 5], [24, 22, 17, 5, 17, 16, 6, 18], [19, 21, 8, 5, 23, 11, 16, 14]], i = 0; i < s.length; i++) t = "", s[i].forEach(function (a, b) {
    t += String.fromCharCode(a + b + 89)
}), s[i] = t;

function startMenuAnimation(a) {
    var b = document.getElementById("miniMenu");
    b.removeAttribute("class");
    b.setAttribute("class", "animate" + (a ? " reverse" : ""));
    a ? b.addEventListener("animationend", endMenuAnimation, !1) : b.children[0].children[0].addEventListener("animationend", endMenuAnimation, !1)
}

function endMenuAnimation(a) {
    this.removeEventListener("animationend", endMenuAnimation);
    document.getElementById("miniMenu").hasAttribute("class") && -1 != document.getElementById("miniMenu").getAttribute("class").indexOf("reverse") && (document.getElementById("miniMenu").style.display = "");
    document.getElementById("miniMenu").removeAttribute("class")
}

function loadNewImage(a) {
    a || (a = document.getElementById("imgPicker").files[0]);
    if (FileReader && "image/" == a.type.substr(0, 6)) {
        var b = new FileReader;
        b.onload = function () {
            fuzzyMode = "data:image/jpeg;" == b.result.substr(0, 16) ? !0 : !1;
            imgPreview.onload = function () {
                setTimeout(1, appraisalMode ? appraiseImageList() : appraiseImage())
            };
            imgPreview.src = b.result;
            imgPreview.setAttribute("data-show", "")
        };
        b.readAsDataURL(a)
    }
}

function prepareCanvas() {
    imgC.width = imgPreview.naturalWidth;
    imgC.height = imgPreview.naturalHeight;
    imgCTX.drawImage(imgPreview, 0, 0, imgPreview.naturalWidth, imgPreview.naturalHeight);
    imageScaleVal = imgPreview.naturalWidth / 720;
    bYoff = ~~(96 * imageScaleVal);
    var a = imgCTX.getImageData(0, imgPreview.naturalHeight - 1, imgPreview.naturalWidth, 1).data,
        b = 4 * (imgPreview.naturalWidth - 1), c = 4 * Math.round(imgPreview.naturalWidth / 2);
    c = [a[c], a[c + 1], a[c + 2]];
    b = [a[b], a[b + 1], a[b + 2]];
    closeEnoughRGB([a[0], a[1], a[2]], c) && closeEnoughRGB(c,
        b) || (bYoff = 0);
    imageMiddle = Math.round(imgPreview.naturalWidth / 2)
}

function appraiseImage() {
    pageContent.setAttribute("class", "hasResults");
    prepareCanvas();
    var a = getBadgeColour();
    if (-1 == a) setResult(polyglot.t("failedBadgeTest"), polyglot.t("tryDifferentImage")); else if (3 == a) setResult(polyglot.t("goldBadgeComment"), ""), buildGraphPicker(3E4); else {
        var b = .25 * imgPreview.naturalHeight, c = findY();
        if (!c || badgePos - c > b) for (var d = 6; (!c || badgePos - c > b) && 20 > d && !(c = findY(~~(imageScaleVal * d)));) d = -d, 0 < d && (d += 6);
        c ? (b = getWidthAndPosition(c)) ? (buildBadgeResults(b[0], b[1], a, b[2]), buildGraphPicker(badgeCols[a][3] +
            Math.round(b[1] / b[0] * badgeCols[a][1]))) : setResult(polyglot.t("failedProgressBarTest"), polyglot.t("tryDifferentImage")) : setResult(polyglot.t("failedProgressBarTest"), polyglot.t("tryDifferentImage"))
    }
}

function buildBadgeResults(a, b, c, d, g) {
    if (g) k = g[0], b = g[1]; else {
        "q" != loctionhostname[0] && (a *= 1.5);
        var k = Math.round(b / a * 100);
        b = badgeCols[c][1] - Math.round(b / a * badgeCols[c][1])
    }
    var e = document.createDocumentFragment();
    if (1 == d) {
        var h = document.createElement("small");
        h.textContent = polyglot.t("obstruction");
        e.appendChild(h)
    }
    h = document.createElement("h4");
    h.textContent = polyglot.t("levelUpYourBadge");
    e.appendChild(h);
    var f = Math.ceil(b / 1E3);
    h = document.createElement("div");
    h.textContent = polyglot.t("completeRaids",
        {smart_count: f});
    e.appendChild(h);
    h = document.createElement("div");
    h.textContent = polyglot.t("placePokemon", {numPokemon: Math.ceil(b / 100)});
    e.appendChild(h);
    h = Math.ceil(b / 60);
    f = Math.floor(h / 24);
    h -= 24 * f;
    f = 0 < f ? polyglot.t("numDays", {smart_count: f}) : !1;
    var l = 0 < h ? polyglot.t("numHours", {smart_count: h}) : !1, p = f && l ? polyglot.t("timeSpacer") : "";
    h = document.createElement("div");
    h.textContent = polyglot.t("inGymFor", {numDays: f ? f : "", timeSpacer: p, numHours: l ? l : ""});
    e.appendChild(h);
    f = Math.ceil(b / 15);
    h = document.createElement("div");
    h.textContent = polyglot.t("defeatGymPokemon", {numPokemon: f, cp: 1500});
    e.appendChild(h);
    f = Math.ceil(b / 10);
    h = document.createElement("div");
    h.textContent = polyglot.t("feedBerries", {smart_count: f});
    e.appendChild(h);
    g ? g[2].appendChild(e) : (d = 2 == d ? polyglot.t("unsure") : "", a = polyglot.t("errorMarginStr", {errorMargin: Math.ceil(1 / a * badgeCols[c][1])}), setResult(polyglot.t("badgePercent", {
        badge: polyglot.t(badgeCols[c][0]),
        unsure: d,
        percent: k
    }), polyglot.t("neededBXP", {neededBXP: b, errorMargin: a})), results.children[3].appendChild(e))
}

function setResult(a, b) {
    results.children[0].textContent = a || "";
    for (results.children[2].textContent = b || ""; results.children[3].firstChild;) results.children[3].removeChild(results.children[3].firstChild)
}

function findY(a) {
    a || (a = 0);
    tmpXoffset = a;
    a = imgCTX.getImageData(imageMiddle + a, 0, 1, imgPreview.naturalHeight).data;
    for (var b, c = [0, 0, 0], d = 0, g = imgPreview.naturalHeight - 1 - bYoff; 0 < g; g--) {
        b = [a[4 * g], a[4 * g + 1], a[4 * g + 2]];
        if (closeEnough(b[0], 21) || closeEnough(b[1], 232)) if (closeEnoughRGB(b, c, fuzzyMode)) 0 == d && (d = 1), d++; else {
            if (d >= minCore && (closeEnoughRGB(c, [232, 232, 232]) || closeEnoughRGBF(c, [21, 232, 219]))) return g - 1 + Math.round(d / 2);
            d = 0
        } else {
            if (d >= minCore && (closeEnoughRGB(c, [232, 232, 232]) || closeEnoughRGBF(c, [21, 232,
                    219]))) return g - 1 + Math.round(d / 2);
            d = 0
        }
        c = b.slice(0)
    }
    return !1
}

function getWidthAndPosition(a, b) {
    for (var c = imgCTX.getImageData(0, a, imgPreview.naturalWid…