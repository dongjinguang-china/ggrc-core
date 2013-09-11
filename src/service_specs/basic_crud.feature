Feature: Basic RESTful CRUD Support

  Background:
    Given service description

  Scenario Outline: HTTP POST and GET
    Given an example "<resource_type>"
    When the example "<resource_type>" is POSTed to its collection
    Then a 201 status code is received
    And the response has a Location header
    And we receive a valid "<resource_type>" in the entity body
    And the received "<resource_type>" matches the one we posted

  Examples: Resources
      | resource_type      |
      | Audit              |
      | Category           |
      | Control            |
      | ControlRisk        |
      | DataAsset          |
      #| Directive          |
      | DirectiveControl   |
      | Contract           |
      | Policy             |
      | Regulation         |
      | Document           |
      | Facility           |
      | Help               |
      | Market             |
      #| Meeting            |
      #| ObjectDocument     |
      #| ObjectPerson       |
      | Objective          |
      | ObjectiveControl   |
      | Option             |
      | OrgGroup           |
      | Person             |
      #| PopulationSample   |
      | Product            |
      | Project            |
      | Program            |
      | ProgramDirective   |
      #| Relationship       |
      #| Request            |
      #| Response           |
      | Risk               |
      | RiskyAttribute     |
      | RiskRiskyAttribute |
      | Section            |
      | SectionObjective   |
      #| SystemOrProcess    |
      | System             |
      | Process            |

