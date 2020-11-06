# -*- coding: utf-8 -*-
"""
Connection screen

This is the text to show the user when they first connect to the game (before
they log in).

To change the login screen in this module, do one of the following:

- Define a function `connection_screen()`, taking no arguments. This will be
  called first and must return the full string to act as the connection screen.
  This can be used to produce more dynamic screens.
- Alternatively, define a string variable in the outermost scope of this module
  with the connection string that should be displayed. If more than one such
  variable is given, Evennia will pick one of them at random.

The commands available to the user when the connection screen is shown
are defined in evennia.default_cmds.UnloggedinCmdSet. The parsing and display
of the screen is done by the unlogged-in "look" command.

"""

from django.conf import settings
from evennia import utils

CONNECTION_SCREEN = """

|r             ;;          ;;             
            ;Kk.        .xK;            
           ,0Oc.        .cO0,           
          .OK;            ;XO'          
         .kWd.  ;,        .dNx.         
        .xN0,   ld.   ..   ,KXd.        
       .dKXd   .ON0kkl,.    oX0o.       
      .dKK0,   oWX0kkoc;.   ,0K0o.      
     .oKOXd.  ,ko'.  .'ox'  .dN00o.     
     lKk0X:   .,       'kc   :XKk0l     
    cKOkNXl        ..,lxo.  .lXWOkKc    
   :X0dKXdl:.   'okxddc'   .:ldXNkOK:   
  ;KXdkWo  ..  :XXl.        .  dWKx0K;  
 ;KNddNX;     .dMXc            ;XWkdXK, 
,0WklKMk.  .'. :XMNd;.    .'.  .kMNddN0,
kW0ckWMk.  .oxcl0WMWWO,'ccxd.  .OMMOlOMk
lNOlOMMNx:;cdxd0WWWMMW0K0xxdc:cOWMWkoKNl
.oNOdXMNkxkdlcxNMWKkx0WMXo:llxO0WMKd0No.
 .dNOkNMXxdkOXWMMMXOxKMMMN0OOOOXMNk0Wd. 
  .xN00WMWOdxO0XWMMMMMMWXOkxxONMWKKWx.  
   .kNKXWMk,cOkckNNWMNNKoxk:'oNMXXNk.   
    .ONNWWo  ';..:Okox0c.;'  :XWWWO.    
     'OWMX:       ;xd0O'     :NWW0'     
      ,0MX:       .dWMK,     :XW0,      
       ;KM0c.      cKNN:   .cKMK;       
        :XMWKd.    lXN0' .cONMX:        
         cXWWK,   :KNO,  ,KWMXc         
          lXMK,  cKx;.   ,KMNl          
          .oNK, :Kd.     .cOl.          
           .d0, ,0o        .            
            .c'  lO,                    
                'dl.                    
               ;x;                      
               :x'                      
                lOdoodo.                
                .lNMMK;                 
                 .oK0:                  
                  .;'.

              |nThe Scrolls 
                  2020

  An Elder Scrolls based mud based on 
          |gEvennia|n by Griatch                

""".format(settings.SERVERNAME, utils.get_evennia_version("short"))
