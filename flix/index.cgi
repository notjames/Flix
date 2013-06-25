#!/usr/bin/perl -Tw

use lib qw(/opt/html/flix/lib);

use DBI;
use strict;
use XML::XPath;
use XML::Simple;
use Carp qw(cluck);
use YAML qw(LoadFile);
use WWW::Netflix::API;
use HTML::Template::Expr;
use CGI qw(:standard :FatalsToBrowser);

my $config_hr = LoadFile('/opt/html/flix/config/flix.yaml');
my $dbh;

if ( $dbh = mysql_connect() )
{
    main();
}

sub main
{
    print header();

    unless ( param('action') )
    {
        render();
    }
    else
    {
        render_ajax();
    }
}

sub render
{
    my $template;

    if ( $template = start_template('flix_index_tmpl.html') )
    {
        my $local_data = get_flix_fromdb();
        my $netflix    = Netflix();
    }
    else
    {
        return();
    }

    print $template->output();

    return(1);
}

sub render_ajax
{

}

sub start_template
{
    my $file     = $config_hr->{templates}.'/'.shift();

    if ( -e $file )
    {
        my $tmpl_obj = HTML::Template::Expr->new(filename => $file);

        say('Opened template: '.$file);
        return($tmpl_obj);
    }
    else
    {
        cluck('Template not found!: '.$file);
    }

    return();
}

sub say
{
    my $msg = shift() || '';

    print STDERR $msg,"\n";

    return();
}

sub explain
{
    my $msg    = shift() || '';
    my $dbglvl = shift() || 0;
}

sub mysql_connect
{
    my $data_source = 'DBI:mysql:'.$config_hr->{mysql}->{db};
    my $username    = $config_hr->{mysql}->{user};
    my $password    = $config_hr->{mysql}->{pass};
    my %attr        = (RaiseError => 1);

    say('Connecting to db...'."\nusername: ".$username.' -> '.$data_source);

    my $dbh = DBI->connect($data_source, $username, $password, \%attr);

    return($dbh) if ( $dbh );
    
    return(0);
}

sub get_flix_fromdb
{
    my $sql = 'select * from flix';
    my $obj;
    
    if ( $obj = $dbh->prepare($sql) )
    {
        my $data = $obj->execute();

        if ( $obj->rows() > 0 )
        {
            $data = $obj->fetchall_hashref('id');
            return($data);
        }
        else
        {
            say('No rows were returned...');
        }
    }
    
    return();
}

sub Netflix
{
     my $netflix = WWW::Netflix::API->new({
           consumer_key    => $config_hr->{netflix}->{oauth_consumer_key},
           consumer_secret => $config_hr->{netflix}->{oauth_secret_key},
#           access_token    => $config_hr->{netflix}->{oauth_token},
#           access_secret   => $config_hr->{netflix}->{oauth_token_secret},
           content_filter  => sub{ use XML::Simple; XMLin(@_) },
                                         });

     $netflix->REST->Users->Feeds;
     $netflix->Get() or die $netflix->content_error;
     print Dumper $netflix->content;

     $netflix->REST->Catalog->Titles->Movies('18704531');
     $netflix->Get() or die $netflix->content_error;
     print Dumper $netflix->content;
}

