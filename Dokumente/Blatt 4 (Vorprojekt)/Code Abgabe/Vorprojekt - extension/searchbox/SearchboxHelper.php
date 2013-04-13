<?php
/**
 * Helper class for the Searchbox component.
 *
 * - register the tab for the search results.
 */
class SearchboxHelper extends OntoWiki_Component_Helper
{
    public function init()
    {   
		// register new tab 'Searchbox'   
		OntoWiki_Navigation::register('searchbox', array(
                'controller' => 'searchbox',     // Controllerclass
                'action'     => 'search',       // action-Method
                'name'       => 'Searchbox ',  // name to display in tab
                'priority'   => 50));         // position       
    }
}
