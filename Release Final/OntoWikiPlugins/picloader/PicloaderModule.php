<?php

class PicloaderModule extends OntoWiki_Module
{	   
    /**
     * Returns the content
     */
    public function getContents()
    {
		$translate   = $this->_owApp->translate;
		$url = new OntoWiki_Url(array('controller' => 'picloader', 'action' => 'picloader'), array());  //set controller      
        $this->view->actionUrl = (string)$url;        
		$this->view->startUpload = $translate->_('Upload Picture'); //set translator
 
        $content            = $this->render('picloader');        //render view
        return $content;
    }

    public function getTitle()
    {
		$translate   = $this->_owApp->translate;
        return $translate->_('PicLoader'); //set plugin titel
    }

    public function shouldShow()
    {
		// only registered users may publish data
		if ($this->_owApp->user->isAnonymousUser())
		{
			return false;
		}
       return true;
    }

}


