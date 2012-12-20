App.Backbone.Model.Picture = Backbone.Model.extend({
    defaults: {
        id: -1,
        filename: "",
        largeUrl: "",
        mediumUrl: "",
        smallUrl: "",
    },
    initialize: function() {
    },
    pictureId: function() { return this.get("id"); },
    largeUrl: function() { return this.get("largeUrl"); },
    mediumUrl: function() { return this.get("mediumUrl"); },
    smallUrl: function() { return this.get("smallUrl"); },
});

// $eof
