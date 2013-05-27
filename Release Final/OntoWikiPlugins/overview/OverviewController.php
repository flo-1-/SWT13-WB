<?php
/**
 * Controller class for the Publishdata component.
 *
 * this is the main component to execute apublishing
 * Developed during a "Software Technik Parktikum 20013" project:
 * http://pcai042.informatik.uni-leipzig.de/~swp13-wb/
 * @author Yves Annanias, Wolf Otto (briefe@wolf-otto.de)
 * @copyright Copyright 2007, strauss esolutions
 * @version 1.0
 * @since 18.05.2013
 */
class OverviewController extends OntoWiki_Controller_Component {
	/*
	 * wenn buchstabe angeklickt wurde,
	 * dann führe query durch
	 * und zeige das ergebnis an
	 */
	public function overviewAction()
		
	{	        		
		// set the main windoe title to 'Overview'
		$this->view->placeholder('main.window.title')->set('Overview');
		// welcher buchstabe wurde gewählt?
		$letter = $this->getParam('letter');
		
		$resultset = '';
		// nur wenn ein buchstabe gewählt wurde, dann...
		if ($letter)
		{
			// erstelle query
			$query = new Erfurt_Sparql_SimpleQuery();
		
			$query->setProloguePart('SELECT ?uri ?label  ')
			   	  ->setWherePart('WHERE { ?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://drw-model.saw-leipzig.de/ImportantPerson> . '.
				'?uri <http://www.w3.org/2000/01/rdf-schema#label> ?label . '.			
				'FILTER regex (?label, "^'.$letter.'", "i") }'.  // ^xyz -> ?label muss mit xyz anfangen!
				'ORDER BY ASC(?label)' );
		
			$efApp 		= Erfurt_App::getInstance();
			$efStore 	= $efApp->getStore();
			// TODO richtiges model wählen, vllt. das aktuell selektierte?
			$model 		= $efStore->getModel( 'http://drw-catalog.saw-leipzig.de/' );
			$resultset 	= $model->sparqlQuery($query);
		}
		
		$this->view->literal = $letter; 
		$this->view->urlOverview = $this->_config->urlBase; // basis_url für alle eigenen links
		$this->view->result = $resultset;		
	}
}
