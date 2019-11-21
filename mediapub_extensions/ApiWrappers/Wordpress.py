import requests
import json
import platform

class Wordpress(object):
    """
    Connection class to the Wordpress API

    This class handles connection and paging requests to the Wordpress API.  It
    requires wp-json (or another json api service).

    Attributes:
        verbose (bool): Controls detail printing to stdout
        base_prod_url (str): The base URL to the production API
        base_stage_url (str): The base URL to the staging API
        headers (str): HTTP headers to accompany the request
    """

    verbose = False #TODO: There are no verbose outputs currently
    base_prod_url =  None
    base_stage_url =  None
    headers = None

    def __init__(self, prod_url='https://seattletimes.com/wp-json/', stage_url='https://staging.seattletimes.com/wp-json/'):
        """
        Connection class for Wordpress API

        Args:
            prod_url (str): The base URL to the production API
            stage_url (str): The base URL to the staging API
        """

        #NOTE: I am not sure if the headers details should be passed in here.
        #TODO: This should probably have some validation at some point.
        self.base_prod_url = prod_url
        self.base_stage_url = stage_url
        self.set_headers()

    def set_headers(self, user_agent='BICrawler/2.0.PA', email='businessintelligence@seattletimes.com'):
        """
        Set the HTTP Headers for the request

        Builds a HTTP Header string to be passed with the request. Currently
        only supports User-Agent and From.

        Args:
            user_agent (str): The user agent
            email (str): The email address for the From
        """

        #TODO: Find generic values to use as default.
        #TODO: This should take in any header key-val
        self.headers = {
                'User-Agent': str(user_agent) + ' (' + platform.platform() + ')',
                'From': email
            }


    def get_posts(self, env='stage', post_id=None, *args, **kwargs):
        """
        Gets posts that match the given criteria

        Args:
            env (str): The enviornment URL to request
            post_id (int): The Wordpress post ID to request a single post
            args (list): additional arguments
            kwargs (dictionary): additional filters for URL params

        Returns:
            posts (list): Posts that match the criteria
        """

        # Build the request URL then add params.
        url = self.__build_posts_url(post_id=post_id, env=env)
        url = self.__add_params(url, args=args, kwargs=kwargs)

        # Only pass the page param if it is set in the kwargs, used to determine if request shoudl iterate through the pages.
        if 'page' in kwargs: posts = self.__get_items(url, kwargs['page'], post_id=post_id)
        else: posts = self.__get_items(url, post_id=post_id)
        return posts

    def get_categories(self):
        #TODO: do this
        raise NotImplementedError("Not yet implemented")

    def get_tags(self):
        #TODO: do this
        raise NotImplementedError("Not yet implemented")

    def get_pages(self):
        #TODO: do this
        raise NotImplementedError("Not yet implemented")

    def __handle_response(self,response):
        # Get the text from the response, or throw an exception if needed.

        #NOTE: if everything worked well we should get the text out of the response
        #NOTE (cont): if not, the IndexError is used to know when to stop iterating,
        #NOTE (cont): everything else is raised as a RuntimeError
        if response.status_code == requests.codes.ok:
            response2 = json.loads(response.text)
            return response2
        else:
            response2 = json.loads(response.text)
            if('code' in response2 and response2['code']=='rest_post_invalid_page_number'):
                raise IndexError(response2['code'])
            else:
                raise RuntimeError(response.reason)

    def __get_items(self, url, page=None, post_id=None):
        # Perform the requests to get the API items.

        iter = False # Flag used to iterate through request pages for more results.
        items = [] # Results are stored in a list so that iterated items can be added to current results

        # If a specific page was requested pull that item and return without iterating
        if page or post_id:
            try:
                print(url)
                response = requests.get(url, self.headers)
                items = self.__handle_response(response)
            except IndexError as e: #TODO: these exceptions should be a bit more robust.
                return []
        # Otherwise iterate through pages until there are no more results.
        else:
            # Add page=1 to the URL params and turn on iteration
            page = 1
            url = url + "page={}".format(page)
            iter = True
            if iter: #TODO remove this extra if.
                while True: #page <= 10: # For testing, only get the first 10 pages instead of all of them. #TODO: remove
                    # Replace the page param with an updated one.
                    #NOTE: This fails to replace on the first iteration since there is no page -1 value found.  Expected.
                    url = url.replace('&page=' + str(page - 1), '&page=' + str(page))
                    # print(url)
                    try:
                        response = requests.get(url, self.headers)
                        items.extend(self.__handle_response(response))
                    except IndexError as e: # when the last page is reached stop iter
                        break
                    page += 1
        return items

    def __build_posts_url(self, env='prod', post_id=None):
        # Construct the API URL (sans params)

        url = self.base_prod_url
        if env != 'prod': # If this is staging, update the URL
            url = self.base_stage_url
        url = url + 'wp/v2/posts/' #TODO: This will need to be a param so I can hit hub/post/

        #NOTE: This assumes a REST-style API with the post_id appended to the  url.
        if post_id is not None:
            url = url + str(post_id) + '/'

        return url

    def __add_params(self, base_url, *args, **kwargs):
        # Add the key-vals to the params.

        #NOTE: I am always adding ? to the URL because it does not hurt if there are no params,
        #NOTE (cont): but then I don't have to put in a check for adding the page param.
        url = base_url + '?'

        # If there are no params return, otherwise add them all to the URL
        if not kwargs: return url
        for arg, val in kwargs['kwargs'].items():
            url = url + "{}={}&".format(arg,val)

        return url

if __name__=="__main__":
    print("Don't call directly.  Install package and import as a class.")
    
    wp = Wordpress()
    posts_stage = wp.get_posts(datalayer=1, per_page=2, env='stage', page=1)
    posts_prod = wp.get_posts(datalayer=1, per_page=10, env='prod', after='2018-05-07T07:30:00', before='2018-05-07T08:30:59')
    # print(json.dumps(posts_prod[0], indent=4))
    print('Prod pulled {} and stage pulled {}'.format(len(posts_prod), len(posts_stage)))
