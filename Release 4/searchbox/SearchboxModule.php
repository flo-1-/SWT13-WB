


<?php

class SearchboxModule extends OntoWiki_Module
{	   
    /**
     * Returns the content
     */
    public function getContents()
    {
		
		$translate   = $this->_owApp->translate;
		
		/*define an action with a controller and a view */
		$url = new OntoWiki_Url(array('controller' => 'searchbox', 'action' => 'search'), array());        
        $this->view->actionUrl = (string)$url;        
		$this->view->searchHint = $translate->_('search item:');
        $this->view->startSearch = $translate->_('start search');
        $this->view->extendTable = $translate->_('Extend Search');
        $this->view->insertSearchItem = $translate->_('Insert Search Item');                       
        /* todo
         * Properties generisch Auflisten!
         * */   

        
		/* get all classes of http://drw-model.saw-leipzig.de/ */
		$query = new Erfurt_Sparql_SimpleQuery();
		$query->setProloguePart('SELECT ?object ?label')->setWherePart(
		 'WHERE{ ?object a  <http://www.w3.org/2002/07/owl#Class> . '. 	
		 '?object <http://www.w3.org/2000/01/rdf-schema#label>  ?label . '.
		 'FILTER (langMatches(lang(?label), "de"))'. 
	     '}');
		$efApp  = Erfurt_App::getInstance();
        $efStore = $efApp->getStore();
		$this->model = $efStore->getModel("http://drw-model.saw-leipzig.de/");	
		$queryResult = $this->model->sparqlQuery($query);
		$string =  '';
		/* bring the results into a more usable form and hand them over to the view*/
		$result = array();
		 foreach($queryResult as $item){
			$string = substr($item["object"], 32);
			$item["object"] = $string;
			$result[] = $item;
		 }
		$this->view->classes = $result;
		
		/* get all properties */
		
		$query->setProloguePart('SELECT ?prop ?class ')->setWherePart(
		 'WHERE{ ?prop <http://www.w3.org/2000/01/rdf-schema#domain>  ?class . '. 
	     '}');
		$queryResult = $this->model->sparqlQuery($query);
		$result = array();
		$row = 0;
		
		/* only use the properties with a http://drw-model.saw-leipzig.de/ Prefix */
		
		foreach($queryResult as $item){
			if (substr($item["prop"],0,32)=="http://drw-model.saw-leipzig.de/"){
				$pstring = substr($item["prop"], 32);
				$cstring = substr($item["class"], 32);
				//$item["label"] = $item["label"];
				$result[$row][0] = $pstring;
				$result[$row][1] = $cstring;
				$row++;
			}
		 }
		 
		 /* hand over the properties to the view */
		 
		$this->view->props = $result;
		
		/* render the view */
	    $content            = $this->render('searchbox');  
        return $content;
    } 
	/* sets the title of the window */
    public function getTitle()
    {
		$translate   = $this->_owApp->translate;
        return $translate->_('Searchbox');
    }

    public function shouldShow()
    {
        return true;
    }
    

}
