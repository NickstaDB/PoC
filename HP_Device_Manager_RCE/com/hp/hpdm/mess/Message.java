package com.hp.hpdm.mess;

import java.io.Serializable;

//Important bits of the com.hp.hpdm.mess.Message class
public class Message implements Serializable {
	private static final long serialVersionUID = -1370767056480903289L;
	private String sessionId;
	private String userName;
	private String password;
	private Request request;
	private Response response;
	private boolean needNotify;
	private boolean toSelf;
	
	public void setRequest(Request r) { request = r; }
}
