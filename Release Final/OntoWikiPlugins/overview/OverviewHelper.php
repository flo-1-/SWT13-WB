<?php
/**
 * Helper class for the overview component.
 *
 * - register tab for informations.
 */
class OverviewHelper extends OntoWiki_Component_Helper
{
    public function init()
    {   
	  // register new tab 'Overview' if user registered 		
	  OntoWiki::getInstance()->getNavigation()->register('overview', array(
             'controller' => 'overview', // Controllerclass
             'action'     => 'overview',   // action-Method in controller-class
             'name'       => 'Alle Personen', // name to display in tab
             'priority'   => -10));       // position        		
    }
}
