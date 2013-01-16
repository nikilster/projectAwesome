
App.Backbone.Model.User = Backbone.Model.extend({
    defaults: {
        id: -1,
        firstName: "",
        lastName: "",
        picture: "",
        description: "",
        visionPrivacy: -1,
        followCount: null,
        followerCount: null,
        follow: null,
    },
    initialize: function() {
        _.bindAll(this, "ajaxFollowSuccess", "ajaxFollowError");
    },
    userId: function() { return this.get("id"); },
    firstName: function() { return this.get("firstName"); },
    lastName: function() { return this.get("lastName"); },
    fullName: function() { return this.firstName() + " " + this.lastName(); },
    picture: function() { return this.get("picture"); },
    description: function() { return this.get("description"); },
    visionPrivacy: function() { return this.get("visionPrivacy"); },
    followCount: function() { return this.get("followCount"); },
    followerCount: function() { return this.get("followerCount"); },
    follow: function() { return this.get("follow"); },

    followUser: function() {
        if (DEBUG) console.log("FOLLOW");
        this.setFollow(true);
    },
    unfollowUser: function() {
        if (DEBUG) console.log("UNFOLLOW");
        this.setFollow(false);
    },
    setFollow: function(follow) {
        if (this.userId() != USER['id']) {
            doAjax("/api/user/" + USER['id'] + "/follow_user",
                    JSON.stringify({
                                    'userId' : this.userId(),
                                    'follow' : follow,
                                    }),
                    this.ajaxFollowSuccess,
                    this.ajaxFollowError
            );
        }
    },
    ajaxFollowSuccess: function(data, textStatus, jqXHR) {
        this.set({
           followCount: data.user.followCount,
           followerCount: data.user.followerCount,
           follow: data.user.follow,
        });
    },
    ajaxFollowError: function(jqXHR, textStatus, errorThrown) {
    },
});

// $eof
