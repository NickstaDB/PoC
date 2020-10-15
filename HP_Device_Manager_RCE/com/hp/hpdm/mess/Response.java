package com.hp.hpdm.mess;

import java.io.Serializable;
import java.util.Vector;

//Important bits of the com.hp.hpdm.mess.Response class
public class Response<T extends Object> implements Serializable {
	private static final long serialVersionUID = -694118798341985373L;
	private Vector<Serializable> contentList;
}
