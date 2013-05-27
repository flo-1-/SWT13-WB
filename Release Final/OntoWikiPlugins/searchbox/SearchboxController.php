<?php
/**
 * Controller class for the Searchbox component.
 *
 * this is the main component to execute a query and show result
 */
class SearchboxController extends OntoWiki_Controller_Component {			
			
		/**
		 * main search Action
		 * - see Helper class and Module class
		 */	
		public function searchAction(){	
		$this->view->noSearchItem = "Geben sie bitte einen Namen ein.";
		$query = new Erfurt_Sparql_SimpleQuery();
		/* propertyString is the value of an invisible editfield in the view (searchbox.phtml) */
		$str = $this->getParam('propertyString');
		/* remove the last ; */
		$str = substr($str,0,-1);
		/* if the string is not empty, it is transformed into a two-dimensional array */
		if(!empty($str)){
		
		$result = array();
		foreach (explode(';', $str) as $piece) {
			$result[] = explode(',', $piece);
		} 
		/*begin of the construction of the query */
		$iterator = 0;
		$prologue = '';
		$where = '';
		$filter = 'FILTER ('; 
		$ressource = '';
		
		foreach ($result as $property){
			$iterator += 1;
			if ($iterator == 1) { 
				$ressource = ('?' . $property[0] . $property[1] . 'URI ');
				$prologue .= ('SELECT ?' . $property[0] . '' . $property[1] . 'label '); 

				$where .= ('WHERE {'. $ressource . 
						   'a ' . 
						   '<http://drw-model.saw-leipzig.de/' . $property[0] . '>. ');
				$where .=  ( $ressource . 
							'<http://www.w3.org/2000/01/rdf-schema#label> ' . 
							'?' . $property[0] . '' . $property[1] . 'label. ');
				if ($property[1] != '') 
							$filter .= ('regex (?' .$property[0] . '' . $property[1] . 'label, "' . $property[1] . '" ' . ', "i" 	)');
				
			}
			else{
				$prologue .= ('?' . $property[0] . $property[1] . 'label ');
				$where .= ( $ressource . 
						   '<http://drw-model.saw-leipzig.de/' . $property[0] . '> ' . 
						   '?' . $property[0] .  $property[1] . 'prop. ');
				$where .= ('?' . $property[0] . $property[1] . 'prop ' .
						   '<http://www.w3.org/2000/01/rdf-schema#label> ' .
						   '?' . $property[0] . $property[1] . 'label. ');
				if ($property[1] != '') 
							$filter .= ('regex (?' .$property[0] . '' . $property[1] . 'label, "' . $property[1] . '" ' . ', "i" 	)');
			} 		
		}
		$filter .= ')';
		if ($filter === "FILTER ()")
		{
				$filter = '';
		}
			
		$where .= $filter;
		$where .= '}'; 
		
		/* query is executed */
		
		 $query = new Erfurt_Sparql_SimpleQuery(); 
		 $query->setProloguePart($prologue)->setWherePart($where);
		 $efApp  = Erfurt_App::getInstance();
         $efStore = $efApp->getStore();
		 $this->model = $efStore->getModel("http://drw-catalog.saw-leipzig.de/");	
		 $queryResult = $this->model->sparqlQuery($query);
		 
		 /* check, if the query returned an array */
		if (is_array($queryResult) && isset ($queryResult[0]) && is_array($queryResult[0])) {
			$header = array_keys($result[0]);
		}
		else {
			$queryresult = 'No Person was found.';					
		}	
		
		/* needed variables for the resultset-header */	
		$queryItems = array();
		
		
		
		foreach ($result as $item){
			$queryItems[]  = "http://drw-model.saw-leipzig.de/" ;//. $result;
		}
		$tableHeader = array();
		foreach($result as $item){
			$tableHeader[] = $item[0] . $item[1] . 'label';
		}
		$this->view->queryItems = $queryItems;
		$this->view->tableHeader = $tableHeader;
		$this->view->urlBase = $this->_config->urlBase;			
				$this->view->queryResult = $queryResult; 
		} 
		}
		
}
