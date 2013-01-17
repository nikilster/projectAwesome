
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

        /* This is a total hack. When we have a proper model data store in 
         * JS, we should be able to set any user and all views of them will
         * update. But right now, we need to manually go in and do this
         */
        if (App.Var.Model.pageMode() == App.Const.PageMode.USER_PROFILE &&
            App.Var.Model.currentUserId() == App.Var.Model.loggedInUserId()) {
            App.Var.Model.user().set({
                followCount: data.me.followCount,
                followerCount: data.me.followerCount,
            });
        }
    },
    ajaxFollowError: function(jqXHR, textStatus, errorThrown) {
    },
});

// $eof
