<?php

class PersonviewModule extends OntoWiki_Module
{
    /**
     * Returns the content
     */
    public function getContents()
    {
		$translate   = $this->_owApp->translate;
		$url = new OntoWiki_Url(array('controller' => 'personview', 'action' => 'personview'), array());        
        $this->view->actionUrl = (string)$url;        
        $this->view->personview = $translate->_('Action');
        $content            = $this->render('Personview'); //
        return $content;
    }

    public function getTitle()
    {
		$translate   = $this->_owApp->translate;
        return $translate->_('Personview');
    }

    public function shouldShow()
    {
        return true;
    }

}


