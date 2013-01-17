
App.Backbone.View.User = Backbone.View.extend({
    tagName: "div",
    sel: {
        TEMPLATE: "#UserTemplate",
        NAME: ".Name",
        FOLLOW_BUTTON: ".FollowButton",
    },
    className: "User",
    initialize: function() {
        _.bindAll(this, "toggleFollow", "gotoUser");
        this.model.bind("change", this.render, this);

        this.render();
    },
    events: function() {
        var _events = {}
        _events["click " + this.sel.FOLLOW_BUTTON] = "toggleFollow";
        _events["click " + this.sel.NAME] = "gotoUser";
        return _events;
    },
    render: function() {
        var follow = this.model.follow();
        if (this.model.userId() == USER.id) {
            follow = null;
        }
        var variables = { userId: this.model.userId(),
                          name: this.model.fullName(),
                          picture: this.model.picture(),
                          description: linkify(this.model.description()),
                          follow: follow };
        var template = _.template($(this.sel.TEMPLATE).html(), variables);
        $(this.el).html(template);
        return this;
    },
    toggleFollow: function() {
        if (this.model.userId() != USER['id']) {
            if (this.model.follow() == true) {
                this.model.unfollowUser();
            } else {
                this.model.followUser();
            }
        }
    },
    gotoUser: function(e) {
        e.stopPropagation();    // prevent propagating to other handlers
        e.preventDefault();     // prevent following link

        App.Var.View.hideUserList();

        var userId = this.model.userId();
        this.trackVisionAnalytics("Go to User", {'userId': userId});
        App.Var.Router.navigate("/user/" + userId, {trigger: true});
    },
    //Mixpanel
    trackVisionAnalytics: function(actionName, properties) {

        var loggedIn = userLoggedIn ? "True" : "False";
        var page = App.Var.Model.pageString();
        var userId = this.model.userId();

        //Optional Argument
        if(typeof properties === 'undefined')
            properties = {};

        var baseProperties = {
            'Logged In': loggedIn,
            'Page': page,
            'User Id': userId
        };

        //Merge Properties
        var allProperties = $.extend(baseProperties, properties);

        //Track
        mixpanel.track(actionName, allProperties);
    }

});

App.Backbone.View.UserList = Backbone.View.extend({
    tagName: "div",
    sel: {
        TEMPLATE: "#UserListTemplate",

        BODY: ".UserListBody",
    },
    initialize: function() {
        assert(typeof this.options.listName != "undefined", "No UserList name");
        this.listName = this.options.listName;

        _.bindAll(this, "renderUser");

        this.render();
    },
    render: function() {
        $(this.el).empty();

        var variables = { listName: this.listName };
        var template = _.template($(this.sel.TEMPLATE).html(), variables);
        $(this.el).html(template);

        this.children = [];
        this.collection.each(this.renderUser);
        $(this.el).find(this.sel.BODY).append(this.children);

        return this;
    },
    renderUser: function(model, index) {
        var userView = new App.Backbone.View.User({model: model});
        this.children.push(userView.el);
    },
});

