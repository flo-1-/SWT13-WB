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
			// startup: get translater and create windowTitel				      
			$translate   = $this->_owApp->translate;
            $windowTitle = $translate->_('Search results');
            $this->view->placeholder('main.window.title')->set($windowTitle);														
			// get search string from input field (searchbox.phtml)
			$nameOfPerson = $this->getParam('nameOfPerson');
						
			if (!empty($nameOfPerson)){
				// create query
				$query = new Erfurt_Sparql_SimpleQuery(); 
				$query->setProloguePart('SELECT ?resourceUri ?Name ?yearOfBirth ?placeOfBirth ?yearOfDeath ?placeOfDeath ?labor') 
					  ->setWherePart('WHERE {'. '?resourceUri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>'. '<http://drw-model.saw-leipzig.de/Person> . '.
											'?resourceUri <http://www.w3.org/2000/01/rdf-schema#label> ?Name . '.			 		
											'?resourceUri <http://drw-model.saw-leipzig.de/yearOfBirth> ?yearOfBirth . '.
											'?resourceUri <http://drw-model.saw-leipzig.de/placeOfBirth> ?placeOfBirth . '.
											'?resourceUri <http://drw-model.saw-leipzig.de/yearOfDeath> ?yearOfDeath . '.
											'?resourceUri <http://drw-model.saw-leipzig.de/placeOfDeath> ?placeOfDeath . '.
											'?resourceUri <http://drw-model.saw-leipzig.de/labor> ?labor . '.
											'FILTER regex (?Name, "'.$nameOfPerson.'", "i" )}');								
				/////////// ToDo:
				// model = DRW-Katalog							
				$this->model = $this->_owApp->selectedModel;
				$queryResult = $this->model->sparqlQuery($query);												
				
				$header = array ();		
				if (is_array($queryResult) && isset ($queryResult[0]) && is_array($queryResult[0])) {
					$header = array_keys($queryResult[0]);
				}else {
					$queryResult = 'No Person was found for "%s".';
					$queryResult = sprintf($translate->_($queryResult), $nameOfPerson);					
				}		
				// set strings to view -> search.phtml can access strings from view		
				$this->view->urlBase = $this->_config->urlBase;			
				$this->view->header = $header;
				$this->view->queryResult = $queryResult;
			} else /* if empty($nameOfPerson) */{
				$this->view->queryResult = $translate->_('Please enter a search item.');
			}
		}	
}
