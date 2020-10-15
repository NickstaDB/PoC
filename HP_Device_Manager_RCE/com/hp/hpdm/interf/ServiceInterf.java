package com.hp.hpdm.interf;

import com.hp.hpdm.mess.Message;
import java.rmi.Remote;
import java.rmi.RemoteException;

//Important bits of the com.hp.hpdm.interf.ServiceInterf class
public interface ServiceInterf extends Remote {
	public Message sendMessage(Message msg) throws RemoteException;
}
