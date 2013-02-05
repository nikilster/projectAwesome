App.Backbone.Model.Picture = Backbone.Model.extend({
    constant: {
        LARGE_WIDTH: 600,
        MEDIUM_WIDTH: 275,
        SMALL_WIDTH: 150,
    },
    defaults: {
        id: -1,
        filename: "",
        largeUrl: "",
        largeWidth: -1,
        largeHeight: -1,
        mediumUrl: "",
        mediumWidth: -1,
        mediumHeight: -1,
        smallUrl: "",
        smallWidth: -1,
        smallHeight: -1,
    },
    initialize: function() {
    },
    pictureId: function() { return this.get("id"); },
    largeUrl: function() { return this.get("largeUrl"); },
    largeWidth: function() { return this.get("largeWidth"); },
    largeHeight: function() { return this.get("largeHeight"); },
    largeRatio: function() { return this.largeWidth() / this.largeHeight(); },
    largeHeightWithWidth: function(width) {
        var w = width;
        if (this.largeWidth() < w) {
            w = this.largeWidth();
        }
        return Math.floor(w / (this.largeRatio()));
    },
    mediumUrl: function() { return this.get("mediumUrl"); },
    mediumWidth: function() { return this.get("mediumWidth"); },
    mediumHeight: function() { return this.get("mediumHeight"); },
    mediumRatio: function() { return this.mediumWidth() / this.mediumHeight(); },
    mediumHeightWithWidth: function(width) {
        var w = width;
        if (this.mediumWidth() < w) {
            w = this.mediumWidth();
        }
        return Math.floor(w / (this.mediumRatio()));
    },
    smallUrl: function() { return this.get("smallUrl"); },
    smallWidth: function() { return this.get("smallWidth"); },
    smallHeight: function() { return this.get("smallHeight"); },
    smallRatio: function() { return this.smallWidth() / this.smallHeight(); },
    smallHeightWithWidth: function(width) {
        var w = width;
        if (this.smallWidth() < w) {
            w = this.smallWidth();
        }
        return Math.floor(w / (this.smallRatio()));
    },
});

// $eof
