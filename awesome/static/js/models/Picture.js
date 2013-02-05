App.Backbone.Model.Picture = Backbone.Model.extend({
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
    largeHeightWithWidth: function(width) {
        return Math.floor(this.largeHeight() / (this.largeWidth() / width));
    },
    mediumUrl: function() { return this.get("mediumUrl"); },
    mediumWidth: function() { return this.get("mediumWidth"); },
    mediumHeight: function() { return this.get("mediumHeight"); },
    mediumHeightWithWidth: function(width) {
        return Math.floor(this.mediumHeight() / (this.mediumWidth() / width));
    },
    smallUrl: function() { return this.get("smallUrl"); },
    smallWidth: function() { return this.get("smallWidth"); },
    smallHeight: function() { return this.get("smallHeight"); },
    smallHeightWithWidth: function(width) {
        return Math.floor(this.smallHeight() / (this.smallWidth() / width));
    },
});

// $eof
