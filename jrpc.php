<?php

define('XMDS', true);
define('XIBO', true);
//include_once("lib/include.php");
// Required Library Files
require_once("lib/app/pdoconnect.class.php");
require_once("lib/app/translationengine.class.php");
require_once("lib/app/debug.class.php");
require_once("lib/app/kit.class.php");
require_once("lib/app/pagemanager.class.php");
require_once("lib/app/menumanager.class.php");
require_once("lib/app/modulemanager.class.php");
require_once("lib/app/permissionmanager.class.php");
require_once("lib/app/formmanager.class.php");
require_once("lib/app/helpmanager.class.php");
require_once("lib/app/responsemanager.class.php");
require_once("lib/app/datemanager.class.php");
require_once("lib/app/app_functions.php");
require_once("lib/data/data.class.php");
require_once("lib/modules/module.interface.php");
require_once("lib/modules/module.class.php");
require_once("lib/app/session.class.php");
require_once("lib/app/cache.class.php");
require_once("lib/app/thememanager.class.php");
require_once("lib/pages/base.class.php");
require_once("3rdparty/parsedown/parsedown.php");
require_once("3rdparty/jdatetime/jdatetime.class.php");
require_once("3rdparty/jsonRpc/jsonRPCServer.php");

// Required Config Files
require_once("config/config.class.php");
require_once("config/db_config.php");

// Sort out Magic Quotes
if (get_magic_quotes_gpc()) 
{
    function stripslashes_deep($value)
    {
        $value = is_array($value) ?
                    array_map('stripslashes_deep', $value) :
                    stripslashes($value);

        return $value;
    }

    $_POST = array_map('stripslashes_deep', $_POST);
    $_GET = array_map('stripslashes_deep', $_GET);
    $_COOKIE = array_map('stripslashes_deep', $_COOKIE);
    $_REQUEST = array_map('stripslashes_deep', $_REQUEST);
}

//include_once("lib/xmds.inc.php");
//parse and init the settings.xml
Config::Load();
// gregm added
syslog(LOG_INFO, "xmdsjrpc after Config::Load()");
require 'lib/service/xmdsjrpc.class.php';

$sk = Config::GetSetting('SERVER_KEY');
//        $sk = '42pzE9';
syslog(LOG_INFO, 'xmdsjrpc - sk : '.$sk);

syslog(LOG_INFO, "in xmdsjrpc");
$jrpc = new XMDSJsonRpc();
jsonRPCServer::handle($jrpc)
    or print 'no request';
?>

