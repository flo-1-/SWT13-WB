<?php

/**
 * Module class for the Searchbox component.
 *
 * this is the main module to start a query
 */
class SearchboxModule extends OntoWiki_Module
{
    /**
     * Returns the Module-content 
     */
    public function getContents() {  
		// Object to translate: english -> german
		$translate   = $this->_owApp->translate;
		// new Url with Controller class and the main searchaction
        $url = new OntoWiki_Url(array('controller' => 'searchbox', 'action' => 'search'), array());
        // set strings to view -> searchbox.phtml can access strings from view
        $this->view->actionUrl = (string)$url;        
        $this->view->searchHint = $translate->_('search item:');
        $this->view->startSearch = $translate->_('start search');
        // render the searchbox.phtml and parse code 
        $content = $this->render('searchbox');                         
        return $content;
    }

	/**
	 * set a Module-Titel
	 */
    public function getTitle(){
		$translate   = $this->_owApp->translate;
        return $translate->_('Searchbox');
    }

	/**
	 *  to display Module
	 */ 
    public function shouldShow(){
       return true;
    }

}


