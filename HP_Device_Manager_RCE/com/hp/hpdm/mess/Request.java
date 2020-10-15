package com.hp.hpdm.mess;

import java.io.Serializable;
import java.util.List;
import java.util.Vector;

//Important bits of the com.hp.hpdm.mess.Request class
public class Request<T extends Object> implements Serializable {
	private static final long serialVersionUID = 4355216224548892129L;
	private int serviceId;
	private Vector<Serializable> paramList;
	
	public void setSeviceId(int s) { serviceId = s; }
	public void setParams(List<Serializable> l) { paramList = new Vector<>(l); }
}
