var URL_REGEXP = new RegExp("^http.*");
var MAX_URL_TEXT_LENGTH = 40;

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

function dateFromUTC(dateAsString)
{         
    var ymdDelimiter = "-";

    if (dateAsString == null) {
        return null;
    }       
    var pattern = new RegExp( "(\\d{4})" + ymdDelimiter + "(\\d{2})" + ymdDelimiter + "(\\d{2})T(\\d{2}):(\\d{2}):(\\d{2})" );
    var parts = dateAsString.match( pattern );

    return new Date( Date.UTC(  
                parseInt( parts[1] )
                , parseInt( parts[2], 10 ) - 1
                , parseInt( parts[3], 10 )
                , parseInt( parts[4], 10 )
                , parseInt( parts[5], 10 )
                , parseInt( parts[6], 10 )
                , 0                 
                ));                 
}

function timeFromToday(date) {
    var diff = Date.now() - date;
    var days = parseInt(diff / (24*3600*1000));
    var hours = parseInt(diff / (3600*1000));
    var minutes = parseInt(diff / (60*1000));
    var seconds = parseInt(diff / (1000));

    if (days > 0) {
        if (days == 1) {
            return days + " day ago";
        } else if (days < 30) {
            return days + " days ago";
        } else if (date.getYear() == Date.today().getYear()) {
            return date.toString("MMM d");
        } else {
            return date.toString("MMM d, yyyy");
        }
    } else if (hours > 0) {
        if (hours == 1) {
            return hours + " hour ago";
        } else {
            return hours + " hours ago";
        }
    } else if (minutes > 0) {
        if (minutes == 1) {
            return minutes + " minute ago";
        } else {
            return minutes + " minutes ago";
        }
    } else if (seconds  > 0 ) {
        if (seconds == 1) {
            return seconds + " second ago";
        } else {
            return seconds + " seconds ago";
        }
    } else {
        return "Just now"
    }
}

// $eof
