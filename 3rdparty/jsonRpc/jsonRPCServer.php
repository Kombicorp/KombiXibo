<?php
/*
					COPYRIGHT

Copyright 2007 Sergio Vaccaro <sergio@inservibile.org>

This file is part of JSON-RPC PHP.

JSON-RPC PHP is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

JSON-RPC PHP is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with JSON-RPC PHP; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/

/**
 * This class build a json-RPC Server 1.0
 * http://json-rpc.org/wiki/specification
 *
 * @author sergio <jsonrpcphp@inservibile.org>
 */
class jsonRPCServer {

	public function __construct()
	{
	  syslog(LOG_INFO, "jsonRPCServer construct");
	}

	/**
	 * This function handle a request binding it to a given object
	 *
	 * @param object $object
	 * @return boolean
	 */
	public static function handle($object) {

	
	      if (!function_exists('getallheaders')) 
	      { 
		syslog(LOG_INFO, "getallheaders");

		function getallheaders() 
		  { 
			$headers = ''; 
		    foreach ($_SERVER as $name => $value) 
		    { 
			if (substr($name, 0, 5) == 'HTTP_') 
			{ 
			    $headers[str_replace(' ', '-', ucwords(strtolower(str_replace('_', ' ', substr($name, 5)))))] = $value; 
			} else if ($name == "CONTENT_TYPE") { 
			    $headers["Content-Type"] = $value; 
			} else if ($name == "CONTENT_LENGTH") { 
			    $headers["Content-Length"] = $value; 
			} 
		    } 
		    return $headers; 
		  } 
	      } 

	      foreach (getallheaders() as $name => $value) {
		syslog(LOG_INFO, "$name: $value");
	      }

//    	      syslog(LOG_INFO, "Request Method : "+$_SERVER['REQUEST_METHOD']);

	      $body = file_get_contents('php://input');
      	      syslog(LOG_INFO, "jsonRPCServer Dumping object : ".$body);
      
		if (
			$_SERVER['REQUEST_METHOD'] != 'POST' || 
			  empty($_SERVER['CONTENT_TYPE']) ||
			  $_SERVER['CONTENT_TYPE'] != 'application/json-rpc'
			) {
			// This is not a JSON-RPC request
			syslog(LOG_INFO, "this is not a JSON-RPC request");
			return false;
		}

				
				
		// reads the input data
		$request = json_decode($body);
		$props = get_object_vars($request);
		$method = "";
		$params = "";
		$id = "";
		
		syslog(LOG_INFO, 'logging props ... ');
		foreach ($props as $key => $value)  {
		    if ($key == 'id') {
		      $id = $value;
		    }
		    if ($key == 'method') {
		      $method = $value;
		    }
		    if ($key == 'params') {
		      $params = $value;
		    }
//		    syslog(LOG_INFO, $key.",".$value);
		}

		foreach ($params as $value)  {
		    syslog(LOG_INFO, " parm : ".$value);
		}
		    
//		$request = json_decode(file_get_contents('php://input'),true);
		if (!is_null($request)) {
		  syslog(LOG_INFO, 'logging rpc method ...');
//		  syslog(LOG_INFO, 'rpc method : '.$method." , ".$params);
		}
		
		
//		// executes the task on local object
		try {
//			if ($result = @call_user_func_array(array($object, $request['method']), $request['params'])) {
			if ($result = @call_user_func_array(array($object, $method), $params)) {
				syslog(LOG_INFO, 'at result : '.$result);
				$response = array (
					'id' => $id,
					'result' => $result,
					'error' => NULL
				);
				$response = json_encode($response);
			} else {
				$response = array (
					'id' => $id,
					'result' => NULL,
					'error' => 'unknown method or incorrect parameters'
				);
				$response = json_encode($response);
			}
		} catch (Exception $e) {
			$response = array (
					'id' => $id,
				'result' => NULL,
				'error' => $e->getMessage()
				);
				$response = json_encode($response);
		}
		//syslog(LOG_INFO, 'jsonRPCServer returnning : '.$response);
		// output the response
		syslog(LOG_INFO, 'returning from handle');

		if (!empty($id)) { // notifications don't want response
			syslog(LOG_INFO, 'here.');
			header('Content-type: application/json-rpc');
			echo $response;
//			$jrpc = json_encode($response);
//			syslog(LOG_INFO, 'here : '.$jrpc);
//			echo json_encode($response);
		//	syslog(LOG_INFO, 'here : '.$response);
		}
		
		// finish
		return true;
	}
}
?>
