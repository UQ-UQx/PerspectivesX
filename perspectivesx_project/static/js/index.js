var React = require('react');
var ReactDOM = require('react-dom');

class ItemComponent extends React.Component {

    //React component to display a single submission Item.
    //Displays the text and author of a Perspective Item


    constructor(props) {
        super(props);
        this.state = {item: props.item}

    }

    render() {
        const liStyle = {
            borderStyle: 'outset',
            backgroundColor: 'lightgrey',
            marginBottom: '10px'
        };
        var dateString = new Date(this.state.item.created_at);
        dateString = dateString.getDate()+"/"+dateString.getMonth()+"/"+dateString.getFullYear();
        return <li key={this.state.item.id} style={liStyle}>
                <div>Item: {this.state.item.item}</div>
            <div>Author:{this.state.item.description.split("from")[1]}</div>
            <div>
                <p><a href = {"/perspectivesX/delete_submission_item/"+this.state.item.id+"/"}>delete</a></p>
                <p style={{textAlign: "right"}}>Submitted on: {dateString}</p>
            </div>
        </li>
    }

}

class CuratedItemComponent extends React.Component {

    //React component to display a single submission Item.
    //Displays the text and author of a Perspective Item


    constructor(props) {
        super(props);
        this.state = {item: props.item}

    }

    render() {
        const liStyle = {
            borderStyle: 'outset',
            backgroundColor: 'lightgrey',
            marginBottom: '10px'
        };
        var dateString = new Date(this.state.item.created_at);
        dateString = dateString.getDate()+"/"+dateString.getMonth()+"/"+dateString.getFullYear();
        return <li key={this.state.item.id} style={liStyle}>
                <div>Item: {this.state.item.item}</div>
            <div>Author:{this.state.item.description.split("from")[1]}</div>
            <div>
                <p><a href = {"/perspectivesX/delete_curated_item/"+this.state.item.id+"/"}>delete</a></p>
                <p style={{textAlign: "right"}}>Submitted on: {dateString}</p>
            </div>
        </li>
    }

}


class PerspectiveComponent extends React.Component {

    constructor(props) {
        super(props);
        this.state = {items: [], curated: [], perspective: props.perspective, activity: props.activity};
    }

    loadItemsFromServer() {
        var cur = this;
        $.ajax({
            url: "/perspectivesX/get_user_submission_items/" + this.state.activity + "/" + this.state.perspective + "/",
            datatype: 'json',
            cache: false,
            success: function (data) {
                this.setState({items: data});
            }.bind(this)
        });
        var cur = this;
        $.ajax({
            url: "/perspectivesX/get_user_curated_items/" + this.state.activity + "/" + this.state.perspective + "/",
            datatype: 'json',
            cache: false,
            success: function (data) {
                this.setState({curated: data});
            }.bind(this)
        });
    }


    componentDidMount() {
        this.loadItemsFromServer();
        // setInterval(()=>this.loadItemsFromServer(),
        //             this.props.pollInterval);
    }

    render() {
        const listStyleType = {
            listStyleType: 'none'
        };
        const containerStyle = {
            marginLeft: "15px",
            marginRight: "15px"
        };

        const columnStyle = {
            marginRight: "10px",
        };
        var itemNodes = this.state.items.map(function (item) {
            return <ItemComponent item={item} key={item.id}/>

        });

        var curatedNodes = this.state.curated.map(function (curated) {
            return <CuratedItemComponent item={curated} key={curated.id}/>
        })
        //if(curatedNodes.length>0 && itemNodes.length>0) {
        if (curatedNodes.length == 0) {
            curatedNodes = <li> No curated items. <br/><a href={"/perspectivesX/display_perspective_items/" + this.state.activity + "/" + this.state.perspective + "/"}
                               className="btn btn-primary btn-md">Start Curating</a></li>;
        }
        var submissionButtonText = "Edit Submission"
        if (itemNodes.length == 0) {
            itemNodes = <li>No submissions items for this perspective.<br/><br/></li>
            ;
            submissionButtonText = "New Submission"
        }
        var url = "/perspectivesX/submission/" + this.props.activityName.replace(" ", "-").toLowerCase() + "/" + this.state.perspective + "/";

        return (
            <div className="container-fluid" style={containerStyle}>
                <div className="row row-eq-height">
                    <div className="col-md-6" style={columnStyle}>
                        <div className="well">
                            <p>Submitted for {this.props.name} :</p>
                            <ul style={listStyleType}>
                                {itemNodes}
                                <a href={url}
                                   className="btn btn-primary btn-md">{submissionButtonText}
                                </a>
                            </ul>
                            <br/>
                            <a href={"/perspectivesX/display_perspective_items/" + this.state.activity + "/" + this.state.perspective + "/"}
                               className="btn btn-primary btn-md">View all</a>
                        </div>
                    </div>
                    <div className="col-md-6">
                        <div className="well">
                            <p>Curated for {this.props.name} :</p>
                            <ul style={listStyleType}>
                                {curatedNodes}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        )

    }
}


class PerspectiveGridComponent extends React.Component {
    constructor(props) {
        super(props);
        this.state = {perspectives: []};

    }

    loadPerspectivesFromServer() {
        var cur = this;
        $.ajax({
            url: "/perspectivesX/get_template_items/" + this.props.activity + "/",
            datatype: 'json',
            cache: false,
            success: function (data) {
                this.setState({perspectives: data});
            }.bind(this)
        });
    }

    componentDidMount() {
        this.loadPerspectivesFromServer();
        // setInterval(()=>this.loadPerspectivesFromServer(),
        //             this.props.pollInterval);
    }

    //take care  of no perspective case
    render() {
        if (this.state.perspectives) {
            var perspectiveNodes = this.state.perspectives.map(
                (perspective) => this.mapPerspectives(perspective, this.props.activity)
            );
            if (perspectiveNodes.length == 0) {
                perspectiveNodes =
                    <div className="alert alert-warning"><h4>Something went wrong</h4><br/> <p>No perspective for this
                        activity ! </p></div>
            }
            return (

                <div className="row">

                    <h3>{this.props.name}</h3>
                    {perspectiveNodes}
                </div>
            )
        }

    }

    mapPerspectives(perspective, activity) {
        return <PerspectiveComponent activity={this.props.activity} perspective={perspective.id} name={perspective.name}
                                     activityName={this.props.name} key={perspective.id}/>;
    }
}

class ActivityGridComponent extends React.Component {

    constructor(props) {
        super(props);
        this.state = {activities: []};
    }

    loadActivitiesFromServer() {
        var cur = this;
        $.ajax({
            url: "/perspectivesX/get_activities/",
            datatype: 'json',
            cache: false,
            success: function (data) {
                this.setState({activities: data});
            }.bind(this)
        });
    }

    componentDidMount() {
        this.loadActivitiesFromServer();
        setInterval(() => this.loadActivitiesFromServer(),
            this.props.pollInterval);
    }

    render() {
        if (this.state.activities) {
            const containerStyle = {
                marginLeft: "15px",
                marginRight: "15px"
            };
            var perspectiveGrids = this.state.activities.map(function (activity) {
                return <PerspectiveGridComponent activity={activity.id} name={activity.title} key={activity.id}/>

            });
            return (

                <div className="container-fluid" style={containerStyle}>
                    {perspectiveGrids}
                </div>
            )
        }

    }
}
ReactDOM.render(<ActivityGridComponent pollInterval={100000000}/>, document.getElementById("container"));



