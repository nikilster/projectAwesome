
App.Backbone.Model.User = Backbone.Model.extend({
    defaults: {
        id: -1,
        firstName: "",
        lastName: "",
        picture: "",
        description: "",
        visionPrivacy: -1,
    },
    initialize: function() {
    },
    userId: function() { return this.get("id"); },
    firstName: function() { return this.get("firstName"); },
    lastName: function() { return this.get("lastName"); },
    fullName: function() { return this.firstName() + " " + this.lastName(); },
    picture: function() { return this.get("picture"); },
    description: function() { return this.get("description"); },
    visionPrivacy: function() { return this.get("visionPrivacy"); },
});

// $eof
