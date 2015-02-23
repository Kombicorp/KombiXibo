<?php

require_once '../../3rdparty/jsonRpc/jsonRPCServer.php';
require 'xmdsjrpc.class.php';

syslog(LOG_INFO, "in xmdsjrpc");
$jrpc = new XMDSJsonRpc();
jsonRPCServer::handle($jrpc)
    or print 'no request';
?>

