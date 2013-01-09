var URL_REGEXP = new RegExp("^http.*");
var MAX_URL_TEXT_LENGTH = 25;

function linkify(text) {
    var words = text.split(" ");
    var len = words.length;
    for (var i = 0 ; i < len ; i++) {
        var word = words[i];
        var match = URL_REGEXP.exec(word);
        if ((match != null) && (match.length == 1) && (match[0] == word)) {
            var urlText = word;
            if (urlText.length > MAX_URL_TEXT_LENGTH) {
                urlText = urlText.substring(0, MAX_URL_TEXT_LENGTH) + "...";
            }
            words[i] = "<a target=\"_blank\" href=\"" + word + "\">" + urlText + "</a>";
        }
    }
    return words.join(" ");
}

// $eof
