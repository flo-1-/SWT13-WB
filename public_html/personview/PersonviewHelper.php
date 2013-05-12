<?php
/**
 * Helper class for the PersonView component.
 *
 * - register the tab for the search results.
 */
class PersonviewHelper extends OntoWiki_Component_Helper
{
    public function init()
    {   
		// register new tab 'PersonView'   
		OntoWiki::getInstance()->getNavigation()->register('personview', array(
                'controller' => 'personview',     // Controllerclass
                'action'     => 'personview',       // action-Method
                'name'       => 'Personview',  // name to display in tab
                'priority'   => 50));         // position       
                
          
    }
}
