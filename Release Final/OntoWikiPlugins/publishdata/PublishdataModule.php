<?php

/**
 * Module class for the Publishdata component.
 *
 * this is the main module to start dopublishAction.
 * Developed during a "Software Technik Parktikum 20013" project:
 * http://pcai042.informatik.uni-leipzig.de/~swp13-wb/
 * @author Yves Annanias, Wolf Otto (briefe@wolf-otto.de)
 * @copyright Copyright 2007, strauss esolutions
 * @version 1.0
 * @since 18.05.2013
 */
class PublishDataModule extends OntoWiki_Module
{    
	/**
     * Returns the Module-content 
     * (little Box on the left side)
     */
    public function getContents() {  	
		// use url in publish.phtml for formular-action	    
        $url = new OntoWiki_Url(
			array('controller' => 'publishdata', 'action' => 'dopublish'), 
			array()
		);       
        $this->view->actionUrl = (string)$url;  
        // use urlBase to load spinner.gif
        $this->view->urlBase = $this->_config->urlBase;	
        // render the searchbox.phtml and parse code 		                             
        $content = $this->render('publish');                         
        return $content;
    }

	/**
	 * set a Module-Titel
	 */
    public function getTitle(){		
        return 'Publish';
    }

	/**
	 *  to display Module
	 */ 
    public function shouldShow(){
		// only registered users may publish data
		if ($this->_owApp->user->isAnonymousUser())
		{
			return false;
		}
       return true;
    }

}


