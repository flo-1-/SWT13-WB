<?php
/**
 * Helper class for the publishdata component.
 *
 * - register tab for informations.
 */
class PublishdataHelper extends OntoWiki_Component_Helper
{
    public function init()
    {   
		// register new tab 'Publishdata' if user registered 
		if (!$this->_owApp->user->isAnonymousUser())  
		{
		  OntoWiki::getInstance()->getNavigation()->register('publishdata', array(
             'controller' => 'publishdata', // Controllerclass
             'action'     => 'dopublish',   // action-Method in controller-class
             'name'       => 'Publishdata', // name to display in tab
             'priority'   => 61));          // position        
		}
    }
}
